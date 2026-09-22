import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


class ModelSettings(BaseModel):
    name: str
    device: str = "auto"
    max_length: int = 512
    batch_size: int = 16


class EmbeddingSettings(BaseModel):
    name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "auto"
    dimension: int = 384


class PipelineSettings(BaseModel):
    chunk_size_sentences: int = 2
    chunk_overlap_sentences: int = 1
    retrieval_top_k: int = 3
    neutral_ambiguity_threshold: float = 0.65
    contradiction_delta_margin: float = 0.15
    high_confidence_contradiction: float = 0.55
    high_confidence_entailment: float = 0.70
    enable_entity_sieve: bool = True
    enable_api_arbitration: bool = True
    enable_claim_decomposition_escalation: bool = True
    syntactic_complexity_threshold: int = 3


class CacheSettings(BaseModel):
    enabled: bool = True
    cache_dir: str = ".cache/dhrill"
    max_size_mb: int = 500
    ttl_seconds: int = 604800


class ProviderConfig(BaseModel):
    model: str
    timeout_sec: float = 5.0
    max_retries: int = 2
    rpm_limit: int = 15


class AppConfig(BaseSettings):
    # API Keys (loaded from environment or .env)
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    
    # Subsystem configs loaded from YAML
    models_nli: ModelSettings = Field(default_factory=lambda: ModelSettings(name="cross-encoder/nli-deberta-v3-small"))
    models_embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    pipeline: PipelineSettings = Field(default_factory=PipelineSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    
    fallback_chain: List[str] = ["gemini", "groq", "openrouter", "local_rule"]
    gemini: ProviderConfig = Field(default_factory=lambda: ProviderConfig(model="gemini-3.8-flash", rpm_limit=12))
    groq: ProviderConfig = Field(default_factory=lambda: ProviderConfig(model="llama-3.3-70b-versatile", rpm_limit=25))
    openrouter: ProviderConfig = Field(default_factory=lambda: ProviderConfig(model="openrouter/free", rpm_limit=15))

    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=(str(Path(__file__).resolve().parent.parent / ".env"), ".env"),
        extra="ignore"
    )


def load_config() -> AppConfig:
    yaml_data: Dict[str, Any] = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f) or {}

    config_kwargs: Dict[str, Any] = {}
    if "models" in yaml_data:
        if "nli" in yaml_data["models"]:
            config_kwargs["models_nli"] = ModelSettings(**yaml_data["models"]["nli"])
        if "embedding" in yaml_data["models"]:
            config_kwargs["models_embedding"] = EmbeddingSettings(**yaml_data["models"]["embedding"])

    if "pipeline" in yaml_data:
        config_kwargs["pipeline"] = PipelineSettings(**yaml_data["pipeline"])

    if "cache" in yaml_data:
        config_kwargs["cache"] = CacheSettings(**yaml_data["cache"])

    if "providers" in yaml_data:
        p = yaml_data["providers"]
        if "fallback_chain" in p:
            config_kwargs["fallback_chain"] = p["fallback_chain"]
        if "gemini" in p:
            config_kwargs["gemini"] = ProviderConfig(**p["gemini"])
        if "groq" in p:
            config_kwargs["groq"] = ProviderConfig(**p["groq"])
        if "openrouter" in p:
            config_kwargs["openrouter"] = ProviderConfig(**p["openrouter"])

    if "server" in yaml_data and "cors_origins" in yaml_data["server"]:
        config_kwargs["cors_origins"] = yaml_data["server"]["cors_origins"]

    return AppConfig(**config_kwargs)


# Global singleton settings
settings = load_config()
