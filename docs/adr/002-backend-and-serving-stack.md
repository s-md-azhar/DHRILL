# ADR 002: Backend and Serving Stack Selection

- **Status**: Accepted
- **Date**: 2026-09-22
- **Author**: Lead ML Systems Architect (DHRILL Core Team)
- **Context**: Backend serving framework and runtime architecture for DHRILL on commodity hardware.

---

## 1. Context and Requirements

DHRILL serves both compute-heavy local ML inference (PyTorch tensor operations, cross-encoder forward passes, dense vector searches) and asynchronous I/O (multi-provider HTTP fallback chains, streaming Server-Sent Events, disk/in-memory cache lookups).

We require:
1. Native integration with PyTorch, Hugging Face Transformers, and numerical computing libraries.
2. High-throughput asynchronous event loop so slow external API network requests or long prompts never block local inference queues.
3. Strict schema validation and auto-generated API contracts (OpenAPI / Swagger) for developer consumption.
4. Minimal memory and CPU overhead.
5. Deterministic, one-command deployment across local Windows/Linux and Docker environments.

---

## 2. Alternatives Considered

| Dimension | FastAPI (ASGI + Uvicorn) | Flask / Gunicorn (WSGI) | Go / Rust Sidecar (Triton / Axum) | Node.js (Express / Fastify) |
| :--- | :--- | :--- | :--- | :--- |
| **Python ML Native** | **First-class** (direct tensor memory sharing) | First-class | Requires IPC / gRPC serialization | Requires child processes / ONNX-js |
| **Async I/O Support** | **Native `async`/`await`** | Poor / Greenlet hacking | Native | Native |
| **Data Validation** | **Pydantic v2 (Rust-backed, sub-ms)** | Manual / Marshmallow | Serde / Structs | Zod / Joi |
| **Memory Footprint** | Low (~45 MB idle base) | Low (~40 MB idle base) | Very Low (~15 MB) | Moderate (~65 MB) |
| **Development Speed** | High | High | Low (complex tensor interop) | Moderate |

---

## 3. Decision

We choose **FastAPI + Uvicorn + Pydantic v2** as the core backend serving stack, complemented by:
- **PyTorch + Hugging Face Transformers** for local DeBERTa-v3 cross-encoder inference (with automatic device routing: CUDA if available, vectorized CPU fallback if absent).
- **Sentence-Transformers / `all-MiniLM-L6-v2`** with PyTorch/NumPy cosine similarity and FAISS for sub-millisecond in-memory context indexing.
- **Python `hashlib` + diskcache / LRU dict** for multi-tier input hash caching.
- **Async HTTP client (`httpx`)** with exponential backoff and jitter for the external provider fallback chain.

---

## 4. Architectural Separation of Concerns

1. **`app/core/`**: Pipeline orchestration, multi-provider fallback client, configuration loader, and caching.
2. **`app/modules/`**: Decoupled, modular ML components:
   - `claim_extractor.py`: Local syntactic clause/dependency parsing + fallback escalation.
   - `retriever.py`: In-memory context chunking and vector similarity search.
   - `nli_engine.py`: DeBERTa-v3 cross-encoder inference and probability calibration.
   - `entity_sieve.py`: Deterministic entity/numeric extraction and diff analysis.
   - `aggregator.py`: Multi-signal fusion, hallucination index calculation, and span mapping.
3. **`app/schemas/`**: Pydantic models guaranteeing type safety across input payloads, claim breakdowns, and inspection reports.
4. **`app/api/`**: REST endpoints (`/api/inspect`, `/api/health`, `/api/demo-cases`, `/api/benchmark`).
