import os
import json
import joblib
import pandas as pd

# Load models and encoders
heading_model = joblib.load("model/heading_model.pkl")
level_model = joblib.load("model/level_model.pkl")
level_encoder = joblib.load("model/level_encoder.pkl")
font_encoder = joblib.load("model/font_encoder.pkl")

# Features used during training
features = ["font_size", "is_bold", "is_title_case", "is_uppercase", "line_len", "font_name_encoded"]

def process_single_file(csv_path, output_path):
    try:
        df = pd.read_csv(csv_path)

        # Handle unknown fonts
        df["font_name_encoded"] = df["font_name"].apply(
            lambda x: x if x in font_encoder.classes_ else "unknown"
        )
        if "unknown" in font_encoder.classes_:
            pass
        else:
            font_encoder.classes_ = list(font_encoder.classes_) + ["unknown"]

        df["font_name_encoded"] = font_encoder.transform(df["font_name_encoded"])

        # Predict is_heading
        X = df[features]
        heading_probs = heading_model.predict_proba(X)[:, 1]
        df["heading_confidence"] = heading_probs
        df["is_heading_pred"] = heading_probs >= 0.5

        # Predict heading level
        heading_df = df[df["is_heading_pred"]].copy()
        if not heading_df.empty:
            X_headings = heading_df[features]
            level_probs = level_model.predict_proba(X_headings)
            level_preds = level_model.predict(X_headings)

            heading_df["predicted_level"] = level_encoder.inverse_transform(level_preds)
            heading_df["level_confidence"] = level_probs.max(axis=1)
        else:
            heading_df["predicted_level"] = pd.Series(dtype=str)
            heading_df["level_confidence"] = pd.Series(dtype=float)

        # Sort by page and y
        heading_df.sort_values(by=["page", "y"], inplace=True)

        # Build outline
        outline = []
        for _, row in heading_df.iterrows():
            outline.append({
                "level": row["predicted_level"] if pd.notna(row["predicted_level"]) else "",
                "text": str(row["text"]).strip(),
                "page": int(row["page"]),
                "heading_confidence": round(float(row["heading_confidence"]), 2),
                "level_confidence": round(float(row["level_confidence"]), 2) if pd.notna(row["level_confidence"]) else 0.0
            })

        result = {
            "title": df.iloc[0]["text"].strip() if len(df) > 0 else "",
            "outline": outline
        }

        # Save JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)

        print(f"[✓] {os.path.basename(csv_path)} → {os.path.basename(output_path)}")

    except Exception as e:
        print(f"[✗] Failed: {csv_path} — {e}")

def predict_all():
    input_dir = "data/features"
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            csv_path = os.path.join(input_dir, file)
            output_filename = file.replace(".csv", ".json")
            output_path = os.path.join(output_dir, output_filename)
            process_single_file(csv_path, output_path)

if __name__ == "__main__":
    predict_all()
