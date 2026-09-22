import logging
import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from app.config import settings

logger = logging.getLogger("dhrill.retriever")


class ContextRetriever:
    """
    Per-Query Contextual Micro-Indexer:
    - Ingests reference document pasted with the query
    - Chunks into overlapping sentence strata
    - Dense vector embedding (all-MiniLM-L6-v2, ~80MB)
    - Hybrid scoring: 0.7 * Dense Cosine + 0.3 * Lexical Overlap
    - Sub-5ms retrieval for typical reference documents
    """

    def __init__(self):
        self._model = None
        self._device = None

    def _get_model(self):
        if self._model is None and SentenceTransformer is not None:
            device = "cuda" if settings.models_embedding.device == "cuda" else "cpu"
            if settings.models_embedding.device == "auto":
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            self._device = device
            logger.info(f"Loading embedding model '{settings.models_embedding.name}' on {device}...")
            try:
                self._model = SentenceTransformer(settings.models_embedding.name, device=device, local_files_only=True)
            except Exception:
                try:
                    self._model = SentenceTransformer(settings.models_embedding.name, device=device)
                except Exception as e:
                    logger.warning(f"Could not load SentenceTransformer: {e}. Using lexical overlap.")
                    self._model = None
        return self._model

    def _chunk_context(self, context_text: str) -> List[Dict[str, Any]]:
        """
        Chunks reference context into overlapping sentence strata.
        """
        # Split into sentences safely avoiding decimals (e.g. 1.73 m2, 30 mg)
        raw_sentences = [
            s.strip() for s in re.split(r'(?:(?<=[!?])|(?<=[^\d]\.)|(?<=[.!?]["\'\)\]]))\s+', context_text) 
            if len(s.strip()) > 5
        ]
        if not raw_sentences:
            if context_text.strip():
                raw_sentences = [context_text.strip()]
            else:
                return []

        chunk_size = settings.pipeline.chunk_size_sentences
        overlap = settings.pipeline.chunk_overlap_sentences
        step = max(1, chunk_size - overlap)

        chunks = []
        chunk_idx = 0
        for i in range(0, len(raw_sentences), step):
            window = raw_sentences[i:i + chunk_size]
            chunk_text = " ".join(window)
            chunks.append({
                "passage_id": f"p_{chunk_idx:02d}",
                "text": chunk_text,
                "source": f"ref_passage:sentences_{i+1}-{i+len(window)}"
            })
            chunk_idx += 1

        return chunks

    def _compute_lexical_overlap(self, query: str, document: str) -> float:
        """
        Token-level Jaccard / BM25 proxy for lexical term overlap.
        """
        q_tokens = set(re.findall(r'\b\w{3,}\b', query.lower()))
        d_tokens = set(re.findall(r'\b\w{3,}\b', document.lower()))
        if not q_tokens or not d_tokens:
            return 0.0
        intersection = q_tokens.intersection(d_tokens)
        return len(intersection) / float(len(q_tokens))

    def index_and_retrieve(
        self,
        reference_context: str,
        claims: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Builds ephemeral micro-index over the reference context and retrieves top-k passages per claim.
        Returns: {claim_id: [RetrievedEvidence, ...]}
        """
        k = top_k or settings.pipeline.retrieval_top_k
        chunks = self._chunk_context(reference_context)
        if not chunks:
            return {c["claim_id"]: [] for c in claims}

        chunk_texts = [c["text"] for c in chunks]
        claim_texts = [c["claim_text"] for c in claims]

        model = self._get_model()
        if model is not None:
            # Dense embedding path
            chunk_embeddings = model.encode(chunk_texts, normalize_embeddings=True, show_progress_bar=False)
            claim_embeddings = model.encode(claim_texts, normalize_embeddings=True, show_progress_bar=False)

            # Cosine similarity matrix: [num_claims, num_chunks]
            dense_sims = np.dot(claim_embeddings, chunk_embeddings.T)
        else:
            # Fallback when sentence-transformers is not yet loaded: pure lexical overlap
            dense_sims = np.zeros((len(claim_texts), len(chunk_texts)))

        retrieval_results = {}
        for i, claim in enumerate(claims):
            c_id = claim["claim_id"]
            c_text = claim["claim_text"]
            scored_passages = []

            for j, chunk in enumerate(chunks):
                dense_score = float(dense_sims[i][j]) if model is not None else 0.0
                lexical_score = self._compute_lexical_overlap(c_text, chunk["text"])
                # Hybrid fusion score
                hybrid_score = (0.7 * dense_score) + (0.3 * lexical_score) if model is not None else lexical_score

                scored_passages.append({
                    "passage_id": chunk["passage_id"],
                    "text": chunk["text"],
                    "similarity_score": round(max(0.0, float(hybrid_score)), 4),
                    "source": chunk["source"]
                })

            # Sort by hybrid score descending
            scored_passages.sort(key=lambda x: x["similarity_score"], reverse=True)
            retrieval_results[c_id] = scored_passages[:k]

        return retrieval_results


context_retriever = ContextRetriever()
