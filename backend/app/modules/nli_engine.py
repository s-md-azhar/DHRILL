import logging
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
except ImportError:
    torch = None
    AutoTokenizer = None
    AutoModelForSequenceClassification = None

from app.config import settings
from app.schemas.models import NLIProbabilities

logger = logging.getLogger("dhrill.nli_engine")


class NLIEngine:
    """
    Local Cross-Encoder NLI Engine:
    - Default model: cross-encoder/nli-deberta-v3-small (44M params, ~150MB weights)
    - Latency: ~15-25ms per batch on GPU, ~60ms on CPU
    - Memory: <250MB VRAM
    - Disentangled attention eliminates position bias
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._device = None
        self._label_map: Dict[str, int] = {}

    def _resolve_device(self) -> str:
        if settings.models_nli.device in ["cuda", "cpu"]:
            return settings.models_nli.device
        if torch is not None and torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _load_model(self):
        if self._model is not None:
            return

        if torch is None or AutoModelForSequenceClassification is None:
            logger.warning("PyTorch / Transformers not installed. NLIEngine will use heuristic fallback.")
            return

        self._device = self._resolve_device()
        model_name = settings.models_nli.name
        logger.info(f"Loading NLI cross-encoder '{model_name}' on device '{self._device}'...")

        try:
            # Try loading from local cache first for zero network delay
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
                self._model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True)
            except Exception:
                # If not cached locally, attempt standard load or fall back
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)
                self._model = AutoModelForSequenceClassification.from_pretrained(model_name)

            self._model.to(self._device)
            self._model.eval()

            # Inspect model label mapping
            # Standard NLI: contradiction, entailment, neutral
            id2label = getattr(self._model.config, "id2label", {})
            normalized_map = {}
            for idx, label in id2label.items():
                lbl_lower = str(label).lower()
                if "entail" in lbl_lower:
                    normalized_map["entailment"] = int(idx)
                elif "contradict" in lbl_lower:
                    normalized_map["contradiction"] = int(idx)
                elif "neut" in lbl_lower:
                    normalized_map["neutral"] = int(idx)

            # Fallback if id2label not explicit
            if len(normalized_map) < 3:
                # Common cross-encoder/nli-deberta-v3 convention: 0=contradiction, 1=entailment, 2=neutral
                normalized_map = {"contradiction": 0, "entailment": 1, "neutral": 2}

            self._label_map = normalized_map
            logger.info(f"Loaded NLI model successfully. Label mapping: {self._label_map}")
        except Exception as e:
            logger.error(f"Failed to load NLI model '{model_name}': {e}. Using fallback.")
            self._model = None

    def predict_pairs(
        self,
        pairs: List[Tuple[str, str]]
    ) -> List[NLIProbabilities]:
        """
        Takes a list of (premise, hypothesis) tuples.
        Returns a list of NLIProbabilities.
        """
        if not pairs:
            return []

        self._load_model()

        if self._model is None or self._tokenizer is None:
            # Deterministic heuristic fallback based on token similarity and polarity negation
            return [self._heuristic_fallback(p, h) for p, h in pairs]

        results = []
        batch_size = settings.models_nli.batch_size
        entail_idx = self._label_map.get("entailment", 1)
        contra_idx = self._label_map.get("contradiction", 0)
        neut_idx = self._label_map.get("neutral", 2)

        for i in range(0, len(pairs), batch_size):
            batch = pairs[i:i + batch_size]
            premises = [p for p, _ in batch]
            hypotheses = [h for _, h in batch]

            with torch.no_grad():
                inputs = self._tokenizer(
                    premises,
                    hypotheses,
                    padding=True,
                    truncation=True,
                    max_length=settings.models_nli.max_length,
                    return_tensors="pt"
                ).to(self._device)

                logits = self._model(**inputs).logits
                probs = F.softmax(logits, dim=-1).cpu().numpy()

                for row in probs:
                    p_entail = float(row[entail_idx])
                    p_contra = float(row[contra_idx])
                    p_neut = float(row[neut_idx])
                    # Normalize to guarantee sum to 1.0
                    total = p_entail + p_contra + p_neut
                    results.append(NLIProbabilities(
                        entailment=round(p_entail / total, 4),
                        neutral=round(p_neut / total, 4),
                        contradiction=round(p_contra / total, 4)
                    ))

        return results

    def _heuristic_fallback(self, premise: str, hypothesis: str) -> NLIProbabilities:
        """
        Deterministic lightweight rule fallback when deep model is initializing or unavailable.
        """
        p_lower = premise.lower()
        h_lower = hypothesis.lower()

        # Negation check
        negation_words = {"not", "never", "no", "cannot", "hardly", "seldom"}
        h_neg = any(f" {nw} " in f" {h_lower} " for nw in negation_words)
        p_neg = any(f" {nw} " in f" {p_lower} " for nw in negation_words)

        # Lexical overlap
        p_words = set(p_lower.split())
        h_words = set(h_lower.split())
        overlap = len(p_words.intersection(h_words)) / max(1, len(h_words))

        if h_neg != p_neg and overlap > 0.5:
            # Polarity inversion with high overlap strongly implies contradiction
            return NLIProbabilities(entailment=0.10, neutral=0.15, contradiction=0.75)
        elif overlap > 0.7:
            return NLIProbabilities(entailment=0.80, neutral=0.15, contradiction=0.05)
        elif overlap > 0.35:
            return NLIProbabilities(entailment=0.45, neutral=0.45, contradiction=0.10)
        else:
            return NLIProbabilities(entailment=0.10, neutral=0.80, contradiction=0.10)


nli_engine = NLIEngine()
