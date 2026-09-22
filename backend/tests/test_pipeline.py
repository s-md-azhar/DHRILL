import pytest
from app.schemas.models import InspectionRequest
from app.core.pipeline import pipeline_engine


@pytest.mark.asyncio
async def test_end_to_end_inspection_with_cache():
    req = InspectionRequest(
        response_text="Metformin is safe down to eGFR of 15 mL/min. Annual creatinine monitoring is required.",
        reference_context="Metformin is contraindicated in patients with an eGFR below 30 mL/min. Serum creatinine must be monitored at least annually.",
        prompt="Check Metformin renal thresholds.",
        use_cache=True
    )

    # First run (miss, executes pipeline)
    resp1 = await pipeline_engine.inspect(req)
    assert resp1.inspection_id is not None
    assert len(resp1.claims) >= 2
    assert resp1.metrics.total_claims >= 2
    assert resp1.metrics.hallucination_score > 0.0

    # Second run (must hit cache)
    resp2 = await pipeline_engine.inspect(req)
    assert resp2.cached is True
    assert resp2.metrics.hallucination_score == resp1.metrics.hallucination_score
    assert len(resp2.claims) == len(resp1.claims)
