import urllib.request
import json
from pathlib import Path

BENCHMARK_PATH = Path(__file__).resolve().parent / "benchmark_data.json"

def fetch_halueval_samples():
    print("Fetching authentic HaluEval samples from RUCAIBox repository...")
    samples = []

    # 1. Fetch 35 QA pairs (70 evaluation instances)
    qa_url = "https://raw.githubusercontent.com/RUCAIBox/HaluEval/main/data/qa_data.json"
    req = urllib.request.Request(qa_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        count = 0
        for line in r:
            line_str = line.decode("utf-8", errors="ignore").strip()
            if not line_str:
                continue
            item = json.loads(line_str)
            knowledge = item.get("knowledge", "").strip()
            question = item.get("question", "").strip()
            right_ans = item.get("right_answer", "").strip()
            hallu_ans = item.get("hallucinated_answer", "").strip()

            if knowledge and right_ans and hallu_ans:
                # Add Truthful pair
                samples.append({
                    "id": f"halueval_qa_{count:03d}_truthful",
                    "category": "question_answering",
                    "premise_context": knowledge,
                    "prompt": question,
                    "response_text": right_ans,
                    "ground_truth_label": "SUPPORTED",
                    "ground_truth_contradiction": False
                })
                # Add Hallucinated pair
                samples.append({
                    "id": f"halueval_qa_{count:03d}_hallucinated",
                    "category": "question_answering",
                    "premise_context": knowledge,
                    "prompt": question,
                    "response_text": hallu_ans,
                    "ground_truth_label": "HALLUCINATED",
                    "ground_truth_contradiction": True
                })
                count += 1
                if count >= 35:
                    break

    print(f"Extracted {count * 2} QA benchmark instances.")

    # 2. Fetch 35 Summarization pairs (70 evaluation instances)
    summ_url = "https://raw.githubusercontent.com/RUCAIBox/HaluEval/main/data/summarization_data.json"
    req = urllib.request.Request(summ_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        count = 0
        for line in r:
            line_str = line.decode("utf-8", errors="ignore").strip()
            if not line_str:
                continue
            item = json.loads(line_str)
            doc = item.get("document", "").strip()
            right_summ = item.get("right_summary", "").strip()
            hallu_summ = item.get("hallucinated_summary", "").strip()

            if doc and right_summ and hallu_summ:
                # Add Truthful summary
                samples.append({
                    "id": f"halueval_summ_{count:03d}_truthful",
                    "category": "summarization",
                    "premise_context": doc,
                    "prompt": "Summarize the document accurately.",
                    "response_text": right_summ,
                    "ground_truth_label": "SUPPORTED",
                    "ground_truth_contradiction": False
                })
                # Add Hallucinated summary
                samples.append({
                    "id": f"halueval_summ_{count:03d}_hallucinated",
                    "category": "summarization",
                    "premise_context": doc,
                    "prompt": "Summarize the document accurately.",
                    "response_text": hallu_summ,
                    "ground_truth_label": "HALLUCINATED",
                    "ground_truth_contradiction": True
                })
                count += 1
                if count >= 35:
                    break

    print(f"Extracted {count * 2} Summarization benchmark instances.")
    print(f"Total authentic benchmark pairs assembled: {len(samples)} (70 Truthful, 70 Hallucinated)")

    with open(BENCHMARK_PATH, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2)
    print(f"Saved expanded benchmark to {BENCHMARK_PATH}")

if __name__ == "__main__":
    fetch_halueval_samples()
