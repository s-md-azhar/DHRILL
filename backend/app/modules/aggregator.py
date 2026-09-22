import logging
from typing import List, Dict, Any, Optional

from app.config import settings
from app.schemas.models import (
    ClaimVerificationResult,
    NLIProbabilities,
    RetrievedEvidence,
    EntityDiscrepancy,
    InspectionMetrics
)

logger = logging.getLogger("dhrill.aggregator")


class SignalAggregator:
    """
    Calibrated Multi-Signal Fusion Engine:
    Combines NLI probabilities, retrieval similarity, symbolic entity sieve,
    and optional provider arbitration to determine claim verdict and global faithfulness.
    """

    def __init__(self):
        pass

    def fuse_claim_signals(
        self,
        claim: Dict[str, Any],
        retrieved_passages: List[Dict[str, Any]],
        nli_probs: Optional[NLIProbabilities],
        entity_conflicts: List[EntityDiscrepancy],
        arbitration_verdict: Optional[Dict[str, Any]] = None
    ) -> ClaimVerificationResult:
        """
        Fuses signals for an individual atomic claim.
        """
        c_id = claim["claim_id"]
        c_text = claim["claim_text"]
        start_char = claim["start_char"]
        end_char = claim["end_char"]

        best_evidence = None
        alt_evidence = []
        if retrieved_passages:
            best = retrieved_passages[0]
            best_evidence = RetrievedEvidence(
                passage_id=best["passage_id"],
                text=best["text"],
                similarity_score=best["similarity_score"],
                source=best["source"]
            )
            for alt in retrieved_passages[1:]:
                alt_evidence.append(RetrievedEvidence(
                    passage_id=alt["passage_id"],
                    text=alt["text"],
                    similarity_score=alt["similarity_score"],
                    source=alt["source"]
                ))

        probs = nli_probs or NLIProbabilities(entailment=0.33, neutral=0.34, contradiction=0.33)

        # 1. Check Symbolic Entity Conflicts (Highest precision signal)
        if entity_conflicts and settings.pipeline.enable_entity_sieve:
            # High priority contradiction from entity/numeric mismatch
            primary_conflict = entity_conflicts[0]
            explanation = f"Entity/Numerical conflict detected: {primary_conflict.description}"
            return ClaimVerificationResult(
                claim_id=c_id,
                claim_text=c_text,
                start_char=start_char,
                end_char=end_char,
                verdict="CONTRADICTED",
                confidence=0.95,
                probabilities=NLIProbabilities(
                    entailment=min(probs.entailment, 0.1),
                    neutral=min(probs.neutral, 0.1),
                    contradiction=0.95
                ),
                best_evidence=best_evidence,
                alternative_evidence=alt_evidence,
                entity_conflicts=entity_conflicts,
                arbitration_source="entity_sieve",
                explanation=explanation
            )

        # 2. Check API Arbitration if triggered
        if arbitration_verdict and arbitration_verdict.get("verdict"):
            v = arbitration_verdict["verdict"].upper()
            expl = arbitration_verdict.get("explanation", "Arbitrated via external frontier model.")
            source = arbitration_verdict.get("arbitration_source", "api_arbitration")
            conf = arbitration_verdict.get("confidence", 0.85)

            return ClaimVerificationResult(
                claim_id=c_id,
                claim_text=c_text,
                start_char=start_char,
                end_char=end_char,
                verdict=v,
                confidence=conf,
                probabilities=probs,
                best_evidence=best_evidence,
                alternative_evidence=alt_evidence,
                entity_conflicts=entity_conflicts,
                arbitration_source=source,
                explanation=expl
            )

        # 3. Local Neural NLI Decision Logic
        p_contra = probs.contradiction
        p_entail = probs.entailment
        p_neut = probs.neutral

        # Condition A: Clear Contradiction
        if p_contra >= settings.pipeline.high_confidence_contradiction:
            verdict = "CONTRADICTED"
            confidence = p_contra
            source = "local_nli"
            ref_snippet = f" Reference asserts: \"{best_evidence.text[:120]}...\"" if best_evidence else ""
            explanation = f"Direct factual contradiction detected (P={p_contra:.2f}).{ref_snippet}"

        # Condition B: Clear Entailment
        elif p_entail >= settings.pipeline.high_confidence_entailment:
            verdict = "VERIFIED"
            confidence = p_entail
            source = "local_nli"
            ref_snippet = f" Grounded in: \"{best_evidence.text[:120]}...\"" if best_evidence else ""
            explanation = f"Factually grounded and entailed by reference (P={p_entail:.2f}).{ref_snippet}"

        # Condition C: Ungrounded Extrinsic Claim
        elif p_neut >= settings.pipeline.neutral_ambiguity_threshold and (not best_evidence or best_evidence.similarity_score < 0.35):
            verdict = "UNGROUNDED"
            confidence = p_neut
            source = "grounding_gap"
            explanation = f"Claim lacks factual support in the reference context (Neutral P={p_neut:.2f}, Low context relevance)."

        # Condition D: Ambiguous
        else:
            verdict = "AMBIGUOUS"
            confidence = max(p_entail, p_contra, p_neut)
            source = "local_nli"
            explanation = f"Insufficient evidence to conclusively verify or refute (Entailment={p_entail:.2f}, Contradiction={p_contra:.2f}, Neutral={p_neut:.2f})."

        return ClaimVerificationResult(
            claim_id=c_id,
            claim_text=c_text,
            start_char=start_char,
            end_char=end_char,
            verdict=verdict,
            confidence=round(float(confidence), 3),
            probabilities=probs,
            best_evidence=best_evidence,
            alternative_evidence=alt_evidence,
            entity_conflicts=entity_conflicts,
            arbitration_source=source,
            explanation=explanation
        )

    def calculate_metrics(self, claim_results: List[ClaimVerificationResult]) -> InspectionMetrics:
        """
        Computes aggregate metrics over all analyzed claims.
        """
        total = len(claim_results)
        if total == 0:
            return InspectionMetrics(
                hallucination_score=0.0,
                faithfulness_score=1.0,
                total_claims=0,
                verified_claims=0,
                contradicted_claims=0,
                ungrounded_claims=0,
                ambiguous_claims=0,
                hallucination_density=0.0
            )

        verified = sum(1 for c in claim_results if c.verdict == "VERIFIED")
        contradicted = sum(1 for c in claim_results if c.verdict == "CONTRADICTED")
        ungrounded = sum(1 for c in claim_results if c.verdict == "UNGROUNDED")
        ambiguous = sum(1 for c in claim_results if c.verdict == "AMBIGUOUS")

        # Hallucination score: full penalty for contradictions, half penalty for ungrounded claims
        h_score = (contradicted + (0.5 * ungrounded)) / float(total)
        faithfulness = verified / float(total)
        density = contradicted / float(total)

        return InspectionMetrics(
            hallucination_score=round(min(1.0, max(0.0, h_score)), 3),
            faithfulness_score=round(min(1.0, max(0.0, faithfulness)), 3),
            total_claims=total,
            verified_claims=verified,
            contradicted_claims=contradicted,
            ungrounded_claims=ungrounded,
            ambiguous_claims=ambiguous,
            hallucination_density=round(density, 3)
        )

    def generate_annotated_spans(self, claim_results: List[ClaimVerificationResult], full_text: str) -> List[Dict[str, Any]]:
        """
        Produces non-overlapping character spans for the frontend highlighter.
        """
        spans = []
        for c in claim_results:
            spans.append({
                "claim_id": c.claim_id,
                "start": c.start_char,
                "end": c.end_char,
                "verdict": c.verdict,
                "confidence": c.confidence,
                "text": full_text[c.start_char:c.end_char] if c.end_char <= len(full_text) else c.claim_text
            })
        # Sort by start offset
        spans.sort(key=lambda s: s["start"])
        return spans


signal_aggregator = SignalAggregator()
