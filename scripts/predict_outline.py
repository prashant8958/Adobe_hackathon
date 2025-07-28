import os
import sys
import json
import joblib
import pandas as pd
import numpy as np  # <-- Required for fix

# Load trained models
heading_model = joblib.load("model/heading_model.pkl")
level_model = joblib.load("model/level_model.pkl")
level_encoder = joblib.load("model/level_encoder.pkl")
font_encoder = joblib.load("model/font_encoder.pkl")

# ✅ FIX: Ensure font_encoder.classes_ is a NumPy array
font_encoder.classes_ = np.array(font_encoder.classes_)

# Define features used during training
features = [
    "font_size", "is_bold", "is_title_case",
    "is_uppercase", "line_len", "font_name_encoded"
]

def predict_outline(csv_path, output_json_path):
    df = pd.read_csv(csv_path)

    # Encode font_name
    df["font_name_encoded"] = df["font_name"].apply(
        lambda x: x if x in font_encoder.classes_ else "unknown"
    )
    if "unknown" in df["font_name_encoded"].values:
        if "unknown" not in font_encoder.classes_:
            font_encoder.classes_ = np.append(font_encoder.classes_, "unknown")
    df["font_name_encoded"] = font_encoder.transform(df["font_name_encoded"])

    # Prepare features
    X = df[features]

    # Predict is_heading with confidence
    heading_probs = heading_model.predict_proba(X)[:, 1]
    df["heading_confidence"] = heading_probs
    df["is_heading_pred"] = heading_probs >= 0.5  # Threshold

    # Predict levels for heading rows
    heading_df = df[df["is_heading_pred"]].copy()
    if not heading_df.empty:
        X_headings = heading_df[features]
        level_probs = level_model.predict_proba(X_headings)
        level_preds = level_model.predict(X_headings)
        heading_df["predicted_level"] = level_encoder.inverse_transform(level_preds)
        heading_df["level_confidence"] = level_probs.max(axis=1)
    else:
        heading_df["predicted_level"] = []
        heading_df["level_confidence"] = []

    # Sort by page and y-coordinate
    heading_df.sort_values(by=["page", "y"], inplace=True)

    # Build outline
    outline = []
    for _, row in heading_df.iterrows():
        outline.append({
            "level": row["predicted_level"],
            "text": str(row["text"]).strip(),
            "page": int(row["page"]),
            "heading_confidence": round(float(row["heading_confidence"]), 2),
            "level_confidence": round(float(row["level_confidence"]), 2)
        })

    output_data = {
        "title": df.iloc[0]["text"].strip() if len(df) > 0 else "",
        "outline": outline
    }

    # Save JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(f"[✓] Saved predicted outline → {output_json_path}")

# CLI usage
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/predict_outline.py <input_csv> <output_json>")
        sys.exit(1)

    csv_file = sys.argv[1]
    output_file = sys.argv[2]
    predict_outline(csv_file, output_file)
