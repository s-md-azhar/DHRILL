import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import router as api_router
from app.modules.nli_engine import nli_engine
from app.modules.retriever import context_retriever

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("dhrill.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: log banner
    logger.info("=" * 60)
    logger.info("  DHRILL: Detection of Hallucination in LLMs  ")
    logger.info(f"  NLI Model:       {settings.models_nli.name}")
    logger.info(f"  Embedding Model: {settings.models_embedding.name}")
    logger.info(f"  Fallback Chain:  {settings.fallback_chain}")
    logger.info("=" * 60)
    yield
    # Shutdown
    logger.info("DHRILL server shutting down.")


app = FastAPI(
    title="DHRILL: Detection of Hallucination in Large Language Models",
    description="Industrial-grade real-time hallucination detection engine featuring local DeBERTa-v3 cross-encoder NLI, contextual micro-indexing, symbolic entity sieving, and multi-provider fallback.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "DHRILL",
        "description": "Detection of Hallucination in Large Language Models",
        "documentation": "/docs",
        "health": "/api/health",
        "demo_cases": "/api/demo-cases"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
