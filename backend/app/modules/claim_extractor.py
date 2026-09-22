import logging
import re
from typing import List, Dict, Any, Optional
from app.config import settings
from app.core.fallback_client import fallback_client

logger = logging.getLogger("dhrill.claim_extractor")


class ClaimExtractor:
    """
    Local-first atomic claim extractor.
    - Default path (100% local): Syntactic clause boundary splitting & span mapping.
    - Escalation path: Only triggered on deeply nested compound sentences when API keys exist.
    """

    # Clause boundary markers
    CONJUNCTION_PATTERN = re.compile(
        r'\b(?:and|but|whereas|while|however|moreover|furthermore|although|though|in addition to)\b',
        re.IGNORECASE
    )
    SEMICOLON_PATTERN = re.compile(r';\s*')
    RELATIVE_CLAUSE_PATTERN = re.compile(r'\b(?:which|who|whom|whose|wherein|whereby)\b', re.IGNORECASE)

    ABBREVIATIONS = {"dr.", "mr.", "mrs.", "ms.", "prof.", "vs.", "etc.", "i.e.", "e.g.", "al."}

    def __init__(self):
        # Boundary pattern:
        # 1. '!' or '?' followed by whitespace: (?<=[!?])\s+
        # 2. Period NOT preceded by a digit followed by whitespace: (?<=[^\d]\.)\s+
        # 3. Punctuation followed by closing quote/bracket then whitespace: (?<=[.!?]["'\)\]])\s+
        self.sentence_boundary_regex = re.compile(
            r'(?:(?<=[!?])|(?<=[^\d]\.)|(?<=[.!?]["\'\)\]]))\s+'
        )

    def _split_into_sentences_with_spans(self, text: str) -> List[Dict[str, Any]]:
        """
        Splits text into sentences while tracking exact [start_char, end_char] offsets.
        Guarantees:
        - Never splits on decimals (e.g., 1.73 m², $3.5M, 0.05).
        - Preserves common honorifics & abbreviations (Dr., vs., etc.).
        - Accurately tracks character offsets in source text.
        """
        if not text or not text.strip():
            return []

        sentences = []
        start_pos = 0

        for match in self.sentence_boundary_regex.finditer(text):
            candidate_end = match.start()
            candidate_text = text[start_pos:candidate_end].strip()

            # Skip split if word before boundary is an abbreviation (e.g., Dr., vs.)
            words = candidate_text.split()
            last_word = words[-1].lower() if words else ""
            if last_word in self.ABBREVIATIONS:
                continue

            if len(candidate_text) >= 2:
                actual_start = start_pos + (len(text[start_pos:candidate_end]) - len(text[start_pos:candidate_end].lstrip()))
                actual_end = actual_start + len(candidate_text)
                sentences.append({
                    "text": candidate_text,
                    "start_char": actual_start,
                    "end_char": actual_end
                })
                start_pos = match.end()

        # Final trailing sentence
        remainder = text[start_pos:].strip()
        if remainder:
            actual_start = start_pos + (len(text[start_pos:]) - len(text[start_pos:].lstrip()))
            sentences.append({
                "text": remainder,
                "start_char": actual_start,
                "end_char": actual_start + len(remainder)
            })

        if not sentences and text.strip():
            sentences.append({
                "text": text.strip(),
                "start_char": 0,
                "end_char": len(text)
            })

        return sentences

    def _calculate_syntactic_complexity(self, sentence: str) -> int:
        """
        Heuristic syntactic complexity metric based on clause density and nesting.
        """
        conjunctions = len(self.CONJUNCTION_PATTERN.findall(sentence))
        semicolons = len(self.SEMICOLON_PATTERN.findall(sentence))
        relatives = len(self.RELATIVE_CLAUSE_PATTERN.findall(sentence))
        word_count = len(sentence.split())
        
        complexity = conjunctions + (semicolons * 2) + relatives
        if word_count > 35:
            complexity += 1
        return complexity

    def _decompose_sentence_locally(self, sentence_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decomposes a single sentence into atomic propositions using rule-based clause splitting,
        preserving the underlying character offsets.
        """
        s_text = sentence_info["text"]
        base_start = sentence_info["start_char"]
        base_end = sentence_info["end_char"]

        # Split on semicolons first
        sub_clauses = []
        last_idx = 0
        for match in self.SEMICOLON_PATTERN.finditer(s_text):
            clause = s_text[last_idx:match.start()].strip()
            if clause:
                sub_clauses.append((clause, base_start + last_idx, base_start + match.start()))
            last_idx = match.end()
        remainder = s_text[last_idx:].strip()
        if remainder:
            sub_clauses.append((remainder, base_start + last_idx, base_end))

        atomic_claims = []
        for clause, c_start, c_end in sub_clauses:
            # Check if clause contains coordinating conjunction connecting complete clauses
            parts = re.split(r',\s*(?:and|but|while|whereas)\s+', clause, flags=re.IGNORECASE)
            if len(parts) > 1 and all(len(p.split()) >= 3 for p in parts):
                curr_offset = c_start
                for p in parts:
                    p_clean = p.strip().rstrip('.')
                    p_len = len(p)
                    if len(p_clean.split()) >= 3:
                        atomic_claims.append({
                            "claim_text": p_clean,
                            "start_char": curr_offset,
                            "end_char": min(curr_offset + p_len, c_end),
                            "is_compound": True,
                            "syntactic_depth": 2
                        })
                    curr_offset += p_len + 5  # approximate delimiter offset
            else:
                clean_claim = clause.strip().rstrip('.')
                if len(clean_claim.split()) >= 2:
                    atomic_claims.append({
                        "claim_text": clean_claim,
                        "start_char": c_start,
                        "end_char": c_end,
                        "is_compound": False,
                        "syntactic_depth": 1
                    })

        return atomic_claims if atomic_claims else [{
            "claim_text": s_text.strip(),
            "start_char": base_start,
            "end_char": base_end,
            "is_compound": False,
            "syntactic_depth": 1
        }]

    async def _decompose_compound_with_api(
        self,
        sentence_info: Dict[str, Any],
        custom_keys: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Escalation path: decomposes highly complex compound sentence via fallback client.
        """
        prompt = f"""Decompose this complex sentence into atomic, standalone factual propositions.
Sentence: "{sentence_info['text']}"

Format as JSON:
{{
  "claims": ["atomic claim 1", "atomic claim 2"]
}}
"""
        raw_resp, provider = await fallback_client.execute_with_fallback(
            prompt,
            custom_keys=custom_keys,
            local_fallback_fn=lambda: {"claims": [c["claim_text"] for c in self._decompose_sentence_locally(sentence_info)]}
        )
        parsed = fallback_client.parse_json_safely(raw_resp)
        claims = parsed.get("claims", [])
        if not claims or not isinstance(claims, list):
            return self._decompose_sentence_locally(sentence_info)

        results = []
        for i, c in enumerate(claims):
            if isinstance(c, str) and len(c.strip()) > 3:
                results.append({
                    "claim_text": c.strip(),
                    "start_char": sentence_info["start_char"],
                    "end_char": sentence_info["end_char"],
                    "is_compound": True,
                    "syntactic_depth": 3,
                    "decomposed_via": provider
                })
        return results if results else self._decompose_sentence_locally(sentence_info)

    async def extract_claims(
        self,
        text: str,
        custom_keys: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extracts atomic claims from passage.
        Local-first by default; escalates to API only for high-complexity compound sentences.
        """
        sentences = self._split_into_sentences_with_spans(text)
        all_claims = []
        claim_counter = 1

        for s_info in sentences:
            complexity = self._calculate_syntactic_complexity(s_info["text"])
            
            # Escalation condition: complexity above threshold AND escalation enabled
            if (
                complexity >= settings.pipeline.syntactic_complexity_threshold
                and settings.pipeline.enable_claim_decomposition_escalation
                and (custom_keys or settings.gemini_api_key or settings.groq_api_key)
            ):
                try:
                    decomposed = await self._decompose_compound_with_api(s_info, custom_keys)
                except Exception as e:
                    logger.warning(f"Escalation failed for sentence '{s_info['text'][:30]}...': {e}. Using local fallback.")
                    decomposed = self._decompose_sentence_locally(s_info)
            else:
                decomposed = self._decompose_sentence_locally(s_info)

            for c in decomposed:
                c["claim_id"] = f"c_{claim_counter:02d}"
                all_claims.append(c)
                claim_counter += 1

        return all_claims


claim_extractor = ClaimExtractor()
