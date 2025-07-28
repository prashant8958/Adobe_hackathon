import csv
import json
import sys
import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict

def normalize(text):
    return text.strip().lower()

def load_labeled_headings(csv_path):
    df = pd.read_csv(csv_path)
    df = df[df["is_heading"] == 1]
    return [
        {
            "text": normalize(row["text"]),
            "page": int(row["page"]),
            "level": row["heading_level"]
        }
        for _, row in df.iterrows()
    ]

def load_predicted_headings(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [
        {
            "text": normalize(item["text"]),
            "page": int(item["page"]),
            "level": item["level"]
        }
        for item in data["outline"]
    ]

def match_predictions(true_headings, predicted_headings, threshold=0.85):
    matched = []
    unmatched_pred = predicted_headings.copy()
    unmatched_true = true_headings.copy()

    for true in true_headings:
        best_match = None
        best_score = 0

        for pred in unmatched_pred:
            if true["page"] != pred["page"]:
                continue
            score = SequenceMatcher(None, true["text"], pred["text"]).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = pred

        if best_match:
            matched.append((true, best_match))
            unmatched_pred.remove(best_match)
            unmatched_true.remove(true)

    return matched, unmatched_true, unmatched_pred

def evaluate(labeled_csv, predicted_json, output_csv):
    true_headings = load_labeled_headings(labeled_csv)
    predicted_headings = load_predicted_headings(predicted_json)

    matched, unmatched_true, unmatched_pred = match_predictions(true_headings, predicted_headings)

    correct = 0
    partial_level_mismatch = 0

    for true, pred in matched:
        if true["level"] == pred["level"]:
            correct += 1
        else:
            partial_level_mismatch += 1

    total_true = len(true_headings)
    total_pred = len(predicted_headings)

    print(f"Total True Headings     : {total_true}")
    print(f"Total Predicted Headings: {total_pred}")
    print(f"Correct Matches         : {correct}")
    print(f"Level Mismatches        : {partial_level_mismatch}")
    print(f"Missed Headings         : {len(unmatched_true)}")
    print(f"False Positives         : {len(unmatched_pred)}")

    accuracy = correct / total_true * 100 if total_true > 0 else 0
    print(f"\n✅ Heading Accuracy: {accuracy:.2f}%")

    # Save mismatches to CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Page", "True Text", "Pred Text", "True Level", "Pred Level"])

        for true, pred in matched:
            if true["level"] != pred["level"]:
                writer.writerow(["Level Mismatch", true["page"], true["text"], pred["text"], true["level"], pred["level"]])
        for true in unmatched_true:
            writer.writerow(["Missed", true["page"], true["text"], "", true["level"], ""])
        for pred in unmatched_pred:
            writer.writerow(["False Positive", pred["page"], "", pred["text"], "", pred["level"]])

    print(f"[✓] Mismatch report saved to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python evaluate_predictions.py <labeled_csv> <predicted_json> <output_csv>")
        sys.exit(1)

    labeled_csv = sys.argv[1]
    predicted_json = sys.argv[2]
    output_csv = sys.argv[3]

    evaluate(labeled_csv, predicted_json, output_csv)
