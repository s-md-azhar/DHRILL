import logging
import time
import uuid
from typing import Dict, Any, Optional, List

from app.config import settings
from app.core.cache import cache_instance
from app.core.fallback_client import fallback_client
from app.modules.claim_extractor import claim_extractor
from app.modules.retriever import context_retriever
from app.modules.nli_engine import nli_engine
from app.modules.entity_sieve import entity_sieve
from app.modules.aggregator import signal_aggregator
from app.schemas.models import (
    InspectionRequest,
    InspectionResponse,
    ClaimVerificationResult
)

logger = logging.getLogger("dhrill.pipeline")


class DHRILLPipeline:
    """
    Master DHRILL Orchestration Pipeline:
    Coordinates caching, extraction, retrieval, local NLI, entity sieving,
    arbitration fallback, and calibrated metric fusion.
    """

    def __init__(self):
        pass

    async def _arbitrate_ambiguous_claim(
        self,
        claim_text: str,
        evidence_text: str,
        custom_keys: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Escalation path: Asks fallback client to arbitrate genuinely ambiguous claim against evidence.
        """
        prompt = f"""You are a rigorous factual consistency arbiter.
Reference Evidence: "{evidence_text}"
Claim: "{claim_text}"

Determine if the claim is:
1. VERIFIED (directly entailed by evidence)
2. CONTRADICTED (directly contradicts evidence)
3. UNGROUNDED (not supported or absent from evidence)

Format as JSON:
{{
  "verdict": "VERIFIED" | "CONTRADICTED" | "UNGROUNDED",
  "confidence": 0.85,
  "explanation": "concise 1-sentence reasoning"
}}
"""
        try:
            raw_resp, provider = await fallback_client.execute_with_fallback(
                prompt,
                custom_keys=custom_keys,
                local_fallback_fn=lambda: {"verdict": "AMBIGUOUS", "confidence": 0.5, "explanation": "Ambiguity arbitration unkeyed."}
            )
            parsed = fallback_client.parse_json_safely(raw_resp)
            if "verdict" in parsed:
                parsed["arbitration_source"] = provider
                return parsed
        except Exception as e:
            logger.warning(f"Arbitration failed for claim '{claim_text[:30]}...': {e}")
        return None

    async def inspect(self, request: InspectionRequest) -> InspectionResponse:
        t0 = time.perf_counter()
        resp_text = request.response_text.strip()
        ref_context = (request.reference_context or "").strip()
        custom_keys = request.custom_api_keys

        # Step 0: SHA-256 Hash Caching
        cache_key = cache_instance.compute_hash(
            response_text=resp_text,
            reference_context=ref_context,
            prompt=request.prompt
        )
        if request.use_cache:
            cached_data = cache_instance.get(cache_key)
            if cached_data:
                cached_data["cached"] = True
                cached_data["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
                cached_data["routing_tier"] = "cache-hit"
                if "telemetry" in cached_data:
                    cached_data["telemetry"]["routing_tier"] = "cache-hit"
                return InspectionResponse(**cached_data)

        # Step 1: Local-First Atomic Claim Extraction
        claims = await claim_extractor.extract_claims(resp_text, custom_keys=custom_keys)

        # Step 2: Context Micro-Indexing & Hybrid Retrieval
        retrieval_map = {}
        if ref_context:
            retrieval_map = context_retriever.index_and_retrieve(ref_context, claims)

        # Step 3: Local NLI Batch Inference
        pairs = []
        for c in claims:
            passages = retrieval_map.get(c["claim_id"], [])
            premise = passages[0]["text"] if passages else ref_context or resp_text
            pairs.append((premise, c["claim_text"]))

        nli_probs_list = nli_engine.predict_pairs(pairs)

        # Step 4 & 5: Entity Sieve & Ambiguity Arbitration
        claim_results: List[ClaimVerificationResult] = []
        active_routing_tier = "local-only"

        for i, c in enumerate(claims):
            c_id = c["claim_id"]
            passages = retrieval_map.get(c_id, [])
            best_passage_text = passages[0]["text"] if passages else ref_context
            probs = nli_probs_list[i] if i < len(nli_probs_list) else None

            # Entity discrepancy check
            conflicts = []
            if settings.pipeline.enable_entity_sieve and best_passage_text:
                conflicts = entity_sieve.inspect_discrepancies(c["claim_text"], best_passage_text)

            # Check if arbitration is required
            # Constraint 4: Don't call API if local NLI + entity pipeline resolved with high confidence
            arbitration_res = None
            if probs and settings.pipeline.enable_api_arbitration and best_passage_text:
                is_ambiguous_neutral = probs.neutral >= settings.pipeline.neutral_ambiguity_threshold and passages and passages[0]["similarity_score"] > 0.45
                is_close_margin = abs(probs.contradiction - probs.entailment) <= settings.pipeline.contradiction_delta_margin
                if (is_ambiguous_neutral or is_close_margin) and not conflicts:
                    # Escalation to external arbitration
                    arbitration_res = await self._arbitrate_ambiguous_claim(c["claim_text"], best_passage_text, custom_keys)
                    if arbitration_res and "arbitration_source" in arbitration_res:
                        active_routing_tier = arbitration_res["arbitration_source"]

            # Fuse signals
            claim_res = signal_aggregator.fuse_claim_signals(
                claim=c,
                retrieved_passages=passages,
                nli_probs=probs,
                entity_conflicts=conflicts,
                arbitration_verdict=arbitration_res
            )
            claim_results.append(claim_res)

        # Step 6: Global Metric Aggregation
        metrics = signal_aggregator.calculate_metrics(claim_results)
        annotated_spans = signal_aggregator.generate_annotated_spans(claim_results, resp_text)

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        device_name = nli_engine._device or "cpu"

        response = InspectionResponse(
            inspection_id=str(uuid.uuid4()),
            cached=False,
            latency_ms=elapsed_ms,
            device_used=device_name,
            routing_tier=active_routing_tier,
            metrics=metrics,
            claims=claim_results,
            annotated_spans=annotated_spans,
            telemetry={
                "routing_tier": active_routing_tier,
                "claims_extracted": len(claims),
                "passages_indexed": len(context_retriever._chunk_context(ref_context)) if ref_context else 0,
                "cache_key": cache_key,
                "nli_model": settings.models_nli.name,
                "embedding_model": settings.models_embedding.name,
                "throttles": fallback_client.get_throttle_status()
            }
        )

        # Store in cache
        if request.use_cache:
            cache_instance.set(cache_key, response.model_dump())

        return response


pipeline_engine = DHRILLPipeline()
