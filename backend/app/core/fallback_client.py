import asyncio
import json
import logging
import os
import random
import re
import time
from typing import Optional, Dict, Any, List, Tuple
import httpx

from app.config import settings

logger = logging.getLogger("dhrill.fallback")


class MultiProviderFallbackClient:
    """
    Resilient multi-provider client with fallback chain:
    Gemini -> Groq -> OpenRouter -> Local Rule Arbiter
    Features:
    - Zero-crash guarantee (always falls back to local rule arbiter)
    - Jittered exponential backoff on HTTP 429 / 503
    - Structured JSON repair and extraction
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=8.0)
        # Request timestamp queues for sliding 60-second window tracking
        self._request_timestamps: Dict[str, List[float]] = {
            "gemini": [],
            "groq": [],
            "openrouter": []
        }
        # Explicit self-throttle thresholds (RPM) before upstream 429s trigger
        self.rpm_limits: Dict[str, int] = {
            "gemini": getattr(settings.gemini, "rpm_limit", 12),
            "groq": getattr(settings.groq, "rpm_limit", 25),
            "openrouter": getattr(settings.openrouter, "rpm_limit", 15)
        }

    async def close(self):
        await self.client.aclose()

    def is_throttled(self, provider: str) -> bool:
        """
        Evaluates rolling 60-second window to proactively throttle before provider 429.
        """
        now = time.time()
        if provider in self._request_timestamps:
            # Purge timestamps older than 60 seconds
            self._request_timestamps[provider] = [t for t in self._request_timestamps[provider] if now - t < 60.0]
            limit = self.rpm_limits.get(provider, 15)
            if len(self._request_timestamps[provider]) >= limit:
                logger.warning(f"[DHRILL Router] Proactively self-throttling '{provider}' ({len(self._request_timestamps[provider])}/{limit} RPM in rolling 60s window). Bypassing to next tier.")
                return True
        return False

    def record_call(self, provider: str):
        if provider in self._request_timestamps:
            self._request_timestamps[provider].append(time.time())

    def get_throttle_status(self) -> Dict[str, Any]:
        now = time.time()
        status = {}
        for p, ts in self._request_timestamps.items():
            active_ts = [t for t in ts if now - t < 60.0]
            self._request_timestamps[p] = active_ts
            status[p] = {
                "active_rpm": len(active_ts),
                "limit_rpm": self.rpm_limits.get(p, 15),
                "throttled": len(active_ts) >= self.rpm_limits.get(p, 15)
            }
        return status

    def _resolve_keys(self, custom_keys: Optional[Dict[str, str]] = None) -> Dict[str, Optional[str]]:
        custom = custom_keys or {}
        return {
            "gemini": custom.get("gemini") or settings.gemini_api_key or os.getenv("GEMINI_API_KEY"),
            "groq": custom.get("groq") or settings.groq_api_key or os.getenv("GROQ_API_KEY"),
            "openrouter": custom.get("openrouter") or settings.openrouter_api_key or os.getenv("OPENROUTER_API_KEY"),
        }

    async def _call_gemini(self, prompt: str, api_key: str, model: str) -> str:
        models_to_try = [model]
        if "gemini-3.8" in model:
            # Secondary model targets if 3.8 encounters temporary 503 high demand spike
            models_to_try.extend(["gemini-2.5-flash", "gemini-flash-latest"])

        last_error = None
        for m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.0,
                    "maxOutputTokens": 1024,
                    "responseMimeType": "application/json"
                }
            }
            try:
                resp = await self.client.post(url, json=payload, headers={"Content-Type": "application/json"})
                if resp.status_code == 429:
                    raise RuntimeError("Gemini Rate Limit (429)")
                if resp.status_code in (404, 503):
                    logger.info(f"Gemini model {m} returned {resp.status_code}, attempting fallback candidate...")
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                last_error = e
                if "Rate Limit" in str(e):
                    raise
        raise last_error or RuntimeError(f"Gemini generation failed for models {models_to_try}")

    async def _call_groq(self, prompt: str, api_key: str, model: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        models_to_try = [model, "qwen/qwen3.8-27b", "openai/gpt-oss-120b"]
        last_error = None
        for m in models_to_try:
            payload = {
                "model": m,
                "messages": [
                    {"role": "system", "content": "You are a precise fact-checking and claim verification assistant. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }
            try:
                resp = await self.client.post(url, json=payload, headers=headers)
                if resp.status_code == 429:
                    raise RuntimeError("Groq Rate Limit (429)")
                if resp.status_code in (400, 404):
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                last_error = e
                if "Rate Limit" in str(e):
                    raise
        raise last_error or RuntimeError(f"Groq generation failed for models {models_to_try}")

    async def _call_openrouter(self, prompt: str, api_key: str, model: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/dhrill/dhrill",
            "X-Title": "DHRILL Verification"
        }
        models_to_try = [model]
        if model == "openrouter/free":
            models_to_try.extend(["meta-llama/llama-3.3-70b-instruct:free", "google/gemini-2.0-flash-exp:free", "mistralai/mistral-7b-instruct:free"])

        last_error = None
        for m in models_to_try:
            payload = {
                "model": m,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            }
            try:
                resp = await self.client.post(url, json=payload, headers=headers)
                if resp.status_code == 429:
                    raise RuntimeError("OpenRouter Rate Limit (429)")
                if resp.status_code in (400, 404):
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                last_error = e
                if "Rate Limit" in str(e):
                    raise
        raise last_error or RuntimeError(f"OpenRouter generation failed for free models {models_to_try}")

    async def execute_with_fallback(
        self,
        prompt: str,
        custom_keys: Optional[Dict[str, str]] = None,
        local_fallback_fn=None
    ) -> Tuple[str, str]:
        """
        Executes prompt through fallback chain with sliding-window self-throttling.
        Chain: Gemini (≤12 RPM) -> Groq (≤25 RPM) -> OpenRouter (≤15 RPM) -> Local Rule Arbiter
        Returns: (raw_response_text, provider_name)
        """
        keys = self._resolve_keys(custom_keys)

        for provider in settings.fallback_chain:
            # Self-throttling check before making any API call
            if provider in ("gemini", "groq", "openrouter") and self.is_throttled(provider):
                logger.info(f"[DHRILL Router] Proactively skipping {provider} due to self-throttle threshold")
                continue

            if provider == "gemini" and keys.get("gemini"):
                for attempt in range(settings.gemini.max_retries):
                    try:
                        text = await self._call_gemini(prompt, keys["gemini"], settings.gemini.model)
                        self.record_call("gemini")
                        logger.info(f"[DHRILL Router] Handled via: GEMINI ({settings.gemini.model})")
                        return text, "gemini"
                    except Exception as e:
                        logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
                        await asyncio.sleep(0.3 * (2 ** attempt) + random.uniform(0.1, 0.2))

            elif provider == "groq" and keys.get("groq"):
                for attempt in range(settings.groq.max_retries):
                    try:
                        text = await self._call_groq(prompt, keys["groq"], settings.groq.model)
                        self.record_call("groq")
                        logger.info(f"[DHRILL Router] Handled via: GROQ ({settings.groq.model})")
                        return text, "groq"
                    except Exception as e:
                        logger.warning(f"Groq attempt {attempt + 1} failed: {e}")
                        await asyncio.sleep(0.3 * (2 ** attempt) + random.uniform(0.1, 0.2))

            elif provider == "openrouter" and keys.get("openrouter"):
                try:
                    text = await self._call_openrouter(prompt, keys["openrouter"], settings.openrouter.model)
                    self.record_call("openrouter")
                    logger.info(f"[DHRILL Router] Handled via: OPENROUTER ({settings.openrouter.model})")
                    return text, "openrouter"
                except Exception as e:
                    logger.warning(f"OpenRouter call failed: {e}")

            elif provider == "local_rule":
                logger.info("[DHRILL Router] Handled via: LOCAL_RULE (Deterministic offline fallback)")
                if local_fallback_fn:
                    res = local_fallback_fn()
                    return (json.dumps(res) if not isinstance(res, str) else res), "local_rule"
                return json.dumps({"status": "local_rule", "arbitration": "unverified"}), "local_rule"

        # Final safety net
        logger.info("[DHRILL Router] All external providers exhausted/throttled. Handled via: LOCAL_RULE")
        if local_fallback_fn:
            res = local_fallback_fn()
            return (json.dumps(res) if not isinstance(res, str) else res), "local_rule"
        return json.dumps({"verdict": "AMBIGUOUS", "explanation": "All external providers offline or throttled; local rule fallback engaged."}), "local_rule"

    @staticmethod
    def parse_json_safely(raw: str) -> Dict[str, Any]:
        """
        Extracts and parses JSON even if surrounded by markdown code blocks.
        """
        raw = raw.strip()
        # Strip markdown ```json ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
        clean_text = match.group(1).strip() if match else raw
        try:
            return json.loads(clean_text)
        except Exception:
            # Try to locate { ... } block
            brace_match = re.search(r"(\{[\s\S]*\})", clean_text)
            if brace_match:
                try:
                    return json.loads(brace_match.group(1))
                except Exception:
                    pass
            # Bracket list [ ... ]
            bracket_match = re.search(r"(\[[\s\S]*\])", clean_text)
            if bracket_match:
                try:
                    return json.loads(bracket_match.group(1))
                except Exception:
                    pass
            return {"error": "Failed to parse JSON", "raw": raw}


fallback_client = MultiProviderFallbackClient()
