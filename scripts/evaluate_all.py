# scripts/evaluate_all.py

import os
import pandas as pd
import json
from difflib import SequenceMatcher

def is_text_match(a, b, threshold=0.8):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def evaluate_all(labeled_dir, predictions_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    summary = []

    for file in os.listdir(labeled_dir):
        if not file.endswith("_labeled.csv"):
            continue

        pdf_id = file.replace("_labeled.csv", "")
        labeled_path = os.path.join(labeled_dir, file)
        # prediction_path = os.path.join(predictions_dir, f"{pdf_id}.json")
        prediction_path = os.path.join(predictions_dir, f"{pdf_id}_adobe.json")

        if not os.path.exists(prediction_path):
            summary.append({"pdf": pdf_id, "status": "Missing prediction"})
            continue

        # Load data
        labeled_df = pd.read_csv(labeled_path)
        with open(prediction_path, "r", encoding="utf-8") as f:
            prediction_data = json.load(f)

        true_headings = [
            {"text": row["text"], "page": int(row["page"]), "level": str(row["level"])}
            for _, row in labeled_df.iterrows()
        ]
        pred_headings = prediction_data.get("outline", [])

        matched = 0
        level_mismatches = 0
        missed = 0
        used = [False] * len(pred_headings)

        for true in true_headings:
            found = False
            for i, pred in enumerate(pred_headings):
                if used[i]:
                    continue
                if pred["page"] == true["page"] and is_text_match(pred["text"], true["text"]):
                    used[i] = True
                    found = True
                    if str(pred["level"]) == true["level"]:
                        matched += 1
                    else:
                        level_mismatches += 1
                    break
            if not found:
                missed += 1

        false_positives = used.count(False)
        total_true = len(true_headings)
        total_pred = len(pred_headings)
        acc = round(100 * matched / total_true, 2) if total_true else 0.0

        summary.append({
            "pdf": pdf_id,
            "total_true": total_true,
            "total_pred": total_pred,
            "correct": matched,
            "level_mismatches": level_mismatches,
            "missed": missed,
            "false_positives": false_positives,
            "heading_accuracy (%)": acc
        })

    summary_path = os.path.join(output_dir, "summary_all_pdfs.csv")
    pd.DataFrame(summary).to_csv(summary_path, index=False)
    print(f"[✓] Saved accuracy summary to {summary_path}")

# Run the evaluation
if __name__ == "__main__":
    evaluate_all("data/labeled", "predictions", "eval_results")
