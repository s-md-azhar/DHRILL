import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from app.schemas.models import (
    InspectionRequest,
    InspectionResponse,
    BenchmarkCase
)
from app.core.pipeline import pipeline_engine
from app.core.cache import cache_instance
from app.modules.nli_engine import nli_engine
from app.api.demo_data import DEMO_CASES, PRECOMPUTED_DEMO_RESULTS
from app.config import settings

logger = logging.getLogger("dhrill.api")

router = APIRouter()


@router.post("/inspect", response_model=InspectionResponse)
async def inspect_generation(request: InspectionRequest):
    """
    Main inspection endpoint. Decomposes response into atomic claims,
    indexes reference context on the fly, executes cross-encoder NLI and entity sieve,
    and returns granular hallucination metrics with span offsets.
    """
    try:
        return await pipeline_engine.inspect(request)
    except Exception as e:
        logger.error(f"Error during inspection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Inspection pipeline failure: {str(e)}")


@router.get("/demo-cases", response_model=List[BenchmarkCase])
async def get_demo_cases():
    """
    Returns curated portfolio benchmark cases across clinical, historical,
    financial, scientific fabrication, and grounded truth categories.
    """
    return DEMO_CASES


@router.get("/demo-cases/{case_id}/inspect", response_model=InspectionResponse)
async def inspect_demo_case(case_id: str):
    """
    Returns instant precomputed inspection result for a demo case.
    Guarantees flawless live presentation even under network loss or quota exhaustion.
    """
    if case_id in PRECOMPUTED_DEMO_RESULTS:
        return InspectionResponse(**PRECOMPUTED_DEMO_RESULTS[case_id])

    # If not precomputed, run live against the case definition
    case = next((c for c in DEMO_CASES if c.case_id == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail=f"Demo case '{case_id}' not found.")

    req = InspectionRequest(
        response_text=case.response_text,
        reference_context=case.reference_context,
        prompt=case.prompt,
        use_cache=True
    )
    return await pipeline_engine.inspect(req)


@router.get("/health")
async def health_check():
    """
    System diagnostic check: GPU acceleration, CUDA availability, device name, and cache metrics.
    """
    cuda_available = False
    device_name = "CPU"
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
    except Exception:
        pass

    return {
        "status": "healthy",
        "service": "DHRILL (Detection of Hallucination in Large Language Models)",
        "version": "1.0.0",
        "gpu": {
            "cuda_available": cuda_available,
            "device_name": device_name,
            "active_device": nli_engine._device or "uninitialized"
        },
        "models": {
            "nli": settings.models_nli.name,
            "embedding": settings.models_embedding.name
        },
        "cache": {
            "enabled": cache_instance.enabled,
            "hits": cache_instance.hits,
            "misses": cache_instance.misses
        }
    }


@router.post("/cache/clear")
async def clear_cache():
    """
    Clears in-memory and disk cache.
    """
    cache_instance.clear()
    return {"message": "Cache cleared successfully."}
