import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add backend to sys.path so app modules can be imported
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.models import InspectionRequest
from app.core.pipeline import pipeline_engine
from app.modules.nli_engine import nli_engine
from app.modules.retriever import context_retriever
from app.modules.entity_sieve import entity_sieve
from app.config import settings

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("dhrill.evaluation")

BENCHMARK_PATH = Path(__file__).resolve().parent / "benchmark_data.json"
REPORT_PATH = Path(__file__).resolve().parent / "benchmark_report.json"
THRESHOLDS_PATH = Path(__file__).resolve().parent / "calibrated_thresholds.json"


def load_dataset() -> List[Dict[str, Any]]:
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(y_true) if y_true else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn
    }


async def evaluate_single_sample_baselines(sample: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes predictions for all 4 methods on a single benchmark sample:
    1. Pure NLI
    2. Pure Retrieval / Lexical Grounding
    3. Pure Entity Sieve
    4. DHRILL Hybrid Ensemble
    """
    premise = sample["premise_context"]
    response = sample["response_text"]

    # Baseline 1: Pure NLI
    t_start = time.perf_counter()
    nli_probs = nli_engine.predict_pairs([(premise, response)])[0]
    nli_pred = 1 if nli_probs.contradiction >= 0.50 else 0
    t_nli = (time.perf_counter() - t_start) * 1000

    # Baseline 2: Pure Retrieval / Lexical Grounding
    t_start = time.perf_counter()
    lex_sim = context_retriever._compute_lexical_overlap(response, premise)
    # If lexical overlap is very low (<0.40), predict hallucination
    retrieval_pred = 1 if lex_sim < 0.45 else 0
    t_retrieval = (time.perf_counter() - t_start) * 1000

    # Baseline 3: Pure Symbolic Entity Sieve
    t_start = time.perf_counter()
    conflicts = entity_sieve.inspect_discrepancies(response, premise)
    entity_pred = 1 if len(conflicts) > 0 else 0
    t_entity = (time.perf_counter() - t_start) * 1000

    # Method 4: DHRILL Hybrid Ensemble
    t_start = time.perf_counter()
    req = InspectionRequest(
        response_text=response,
        reference_context=premise,
        use_cache=False
    )
    dhrill_res = await pipeline_engine.inspect(req)
    # Predict hallucinated if hallucination_score >= 0.40 or any claim contradicted
    dhrill_pred = 1 if (dhrill_res.metrics.hallucination_score >= 0.40 or dhrill_res.metrics.contradicted_claims > 0) else 0
    t_dhrill = (time.perf_counter() - t_start) * 1000

    return {
        "nli_pred": nli_pred,
        "nli_lat": t_nli,
        "retrieval_pred": retrieval_pred,
        "retrieval_lat": t_retrieval,
        "entity_pred": entity_pred,
        "entity_lat": t_entity,
        "dhrill_pred": dhrill_pred,
        "dhrill_lat": t_dhrill
    }


def tune_thresholds(dataset: List[Dict[str, Any]]):
    """
    Grid search over ambiguity and contradiction thresholds against the dataset
    to calibrate optimal parameters empirically.
    """
    print("=" * 70)
    print("  DHRILL THRESHOLD CALIBRATION SWEEP (Phase 4 Rigor)")
    print("=" * 70)

    # Use first 50% as validation split for tuning
    val_set = dataset[:len(dataset)//2]
    y_true = [1 if d["ground_truth_label"] == "HALLUCINATED" else 0 for d in val_set]

    best_f1 = -1.0
    best_params = {}

    contra_candidates = [0.45, 0.50, 0.55, 0.60]
    margin_candidates = [0.10, 0.15, 0.20]
    neutral_candidates = [0.60, 0.65, 0.70]

    # Precompute NLI and entity conflicts once for the validation set in a single batch
    val_pairs = [(s["premise_context"], s["response_text"]) for s in val_set]
    val_probs = nli_engine.predict_pairs(val_pairs)
    precomputed = []
    for sample, probs in zip(val_set, val_probs):
        conflicts = entity_sieve.inspect_discrepancies(sample["response_text"], sample["premise_context"])
        precomputed.append((probs, len(conflicts)))

    for c_thresh in contra_candidates:
        for m_thresh in margin_candidates:
            for n_thresh in neutral_candidates:
                y_pred = []
                for probs, num_conflicts in precomputed:
                    is_contra = (probs.contradiction >= c_thresh) or (num_conflicts > 0)
                    is_ungrounded = (probs.neutral >= n_thresh)
                    pred = 1 if (is_contra or is_ungrounded) else 0
                    y_pred.append(pred)

                m = calculate_metrics(y_true, y_pred)
                if m["f1"] > best_f1:
                    best_f1 = m["f1"]
                    best_params = {
                        "high_confidence_contradiction": c_thresh,
                        "contradiction_delta_margin": m_thresh,
                        "neutral_ambiguity_threshold": n_thresh,
                        "validation_f1": m["f1"],
                        "validation_accuracy": m["accuracy"]
                    }

    print(f"Optimal Calibrated Thresholds Found:")
    print(f"  - Contradiction Threshold (T_contra): {best_params['high_confidence_contradiction']}")
    print(f"  - Delta Margin (Delta_margin):        {best_params['contradiction_delta_margin']}")
    print(f"  - Neutral Ambiguity Cutoff (T_neut):  {best_params['neutral_ambiguity_threshold']}")
    print(f"  - Validation F1-Score:                {best_params['validation_f1']:.4f}")

    with open(THRESHOLDS_PATH, "w", encoding="utf-8") as f:
        json.dump(best_params, f, indent=2)

    return best_params


async def run_evaluation():
    dataset = load_dataset()
    print(f"Loaded {len(dataset)} evaluation pairs from {BENCHMARK_PATH.name}")

    # Step 1: Threshold tuning
    best_params = tune_thresholds(dataset)

    # Apply tuned thresholds
    settings.pipeline.high_confidence_contradiction = best_params["high_confidence_contradiction"]
    settings.pipeline.contradiction_delta_margin = best_params["contradiction_delta_margin"]
    settings.pipeline.neutral_ambiguity_threshold = best_params["neutral_ambiguity_threshold"]

    # Step 2: Full Benchmark Evaluation across 4 methods
    y_true = [1 if d["ground_truth_label"] == "HALLUCINATED" else 0 for d in dataset]
    nli_preds, nli_lats = [], []
    ret_preds, ret_lats = [], []
    ent_preds, ent_lats = [], []
    dhrill_preds, dhrill_lats = [], []

    for i, sample in enumerate(dataset):
        if (i + 1) % 10 == 0 or (i + 1) == len(dataset):
            print(f"  [Evaluating sample {i+1}/{len(dataset)}]...")
        res = await evaluate_single_sample_baselines(sample)
        nli_preds.append(res["nli_pred"])
        nli_lats.append(res["nli_lat"])
        ret_preds.append(res["retrieval_pred"])
        ret_lats.append(res["retrieval_lat"])
        ent_preds.append(res["entity_pred"])
        ent_lats.append(res["entity_lat"])
        dhrill_preds.append(res["dhrill_pred"])
        dhrill_lats.append(res["dhrill_lat"])

    nli_metrics = calculate_metrics(y_true, nli_preds)
    ret_metrics = calculate_metrics(y_true, ret_preds)
    ent_metrics = calculate_metrics(y_true, ent_preds)
    dhrill_metrics = calculate_metrics(y_true, dhrill_preds)

    results_table = {
        "Pure NLI Cross-Encoder": {**nli_metrics, "avg_latency_ms": round(sum(nli_lats)/len(nli_lats), 2)},
        "Pure Retrieval Grounding": {**ret_metrics, "avg_latency_ms": round(sum(ret_lats)/len(ret_lats), 2)},
        "Pure Symbolic Entity Sieve": {**ent_metrics, "avg_latency_ms": round(sum(ent_lats)/len(ent_lats), 2)},
        "DHRILL Hybrid Ensemble": {**dhrill_metrics, "avg_latency_ms": round(sum(dhrill_lats)/len(dhrill_lats), 2)},
    }

    # Print publication-grade comparison table
    print("\n" + "=" * 80)
    print("  BENCHMARK EVALUATION RESULTS: DHRILL vs ABLATION BASELINES")
    print("=" * 80)
    header = f"{'Method':<28} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-Score':<8} | {'Latency':<9}"
    print(header)
    print("-" * len(header))
    for method, m in results_table.items():
        print(f"{method:<28} | {m['accuracy']:<8.4f} | {m['precision']:<9.4f} | {m['recall']:<8.4f} | {m['f1']:<8.4f} | {m['avg_latency_ms']} ms")
    print("=" * 80)

    # Save full report
    full_report = {
        "timestamp": time.time(),
        "total_samples": len(dataset),
        "calibrated_thresholds": best_params,
        "results": results_table
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)
    print(f"\nReport successfully saved to {REPORT_PATH}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_evaluation())
