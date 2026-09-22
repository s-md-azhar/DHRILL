from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NLIProbabilities(BaseModel):
    entailment: float = Field(..., description="Probability of entailment (0.0 to 1.0)")
    neutral: float = Field(..., description="Probability of neutral/no relationship (0.0 to 1.0)")
    contradiction: float = Field(..., description="Probability of direct contradiction (0.0 to 1.0)")


class RetrievedEvidence(BaseModel):
    passage_id: str
    text: str
    similarity_score: float
    source: str


class EntityDiscrepancy(BaseModel):
    entity_type: str  # "DATE", "NUMBER", "PERCENT", "PERSON", "ORG", "GPE", etc.
    claim_value: str
    context_value: Optional[str] = None
    discrepancy_type: str  # "NUMERICAL_MISMATCH", "DATE_MISMATCH", "UNGROUNDED_ENTITY"
    description: str


class ClaimVerificationResult(BaseModel):
    claim_id: str
    claim_text: str
    start_char: int
    end_char: int
    verdict: str  # "VERIFIED", "CONTRADICTED", "UNGROUNDED", "AMBIGUOUS"
    confidence: float
    probabilities: NLIProbabilities
    best_evidence: Optional[RetrievedEvidence] = None
    alternative_evidence: List[RetrievedEvidence] = Field(default_factory=list)
    entity_conflicts: List[EntityDiscrepancy] = Field(default_factory=list)
    arbitration_source: str  # "local_nli", "entity_sieve", "gemini", "groq", "local_rule", "cached"
    explanation: str


class InspectionMetrics(BaseModel):
    hallucination_score: float = Field(..., description="Composite hallucination index (0.0=pure truth, 1.0=pure fabrication)")
    faithfulness_score: float = Field(..., description="Degree of grounding against reference (0.0 to 1.0)")
    total_claims: int
    verified_claims: int
    contradicted_claims: int
    ungrounded_claims: int
    ambiguous_claims: int
    hallucination_density: float


class InspectionRequest(BaseModel):
    response_text: str = Field(..., min_length=1, description="The LLM generation to inspect for hallucinations")
    reference_context: Optional[str] = Field(None, description="Optional ground-truth reference context or source document")
    prompt: Optional[str] = Field(None, description="Optional user prompt that triggered the generation")
    use_cache: bool = True
    custom_api_keys: Optional[Dict[str, str]] = None


class InspectionResponse(BaseModel):
    inspection_id: str
    cached: bool
    latency_ms: float
    device_used: str
    routing_tier: str = Field(default="local-only", description="Tier that resolved query: cache-hit | local-only | gemini | groq | openrouter | local_rule")
    metrics: InspectionMetrics
    claims: List[ClaimVerificationResult]
    annotated_spans: List[Dict[str, Any]]
    telemetry: Dict[str, Any] = Field(default_factory=dict)


class BenchmarkCase(BaseModel):
    case_id: str
    title: str
    category: str  # "medical", "history", "finance", "science", "grounded_truth"
    prompt: str
    response_text: str
    reference_context: str
    expected_hallucinations: List[str]
    description: str
