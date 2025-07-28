import os
import json
import pandas as pd

features_dir = "data/features"
output_dir = "data/output"
labeled_dir = "data/labeled"  # NEW labeled folder

# Ensure the labeled directory exists
os.makedirs(labeled_dir, exist_ok=True)

for i in range(1, 6):  # Loop from p1 to p5
    csv_path = os.path.join(features_dir, f"p{i}_adobe.csv")
    json_path = os.path.join(output_dir, f"json_{i}.json")
    labeled_csv_path = os.path.join(labeled_dir, f"p{i}_labeled.csv")

    if not os.path.exists(csv_path) or not os.path.exists(json_path):
        print(f"[!] Skipping p{i} — Missing CSV or JSON.")
        continue

    # Load the CSV
    df = pd.read_csv(csv_path)
    df["is_heading"] = 0
    df["heading_level"] = ""

    # Load the JSON outline
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        outline = data.get("outline", [])

    for heading in outline:
        h_text = heading["text"].strip().lower()
        h_page = heading["page"]
        h_level = heading["level"]

        match = df[
            (df["page"] == h_page) &
            (df["text"].str.strip().str.lower() == h_text)
        ]

        df.loc[match.index, "is_heading"] = 1
        df.loc[match.index, "heading_level"] = h_level

    # Save to labeled folder
    df.to_csv(labeled_csv_path, index=False)
    print(f"[✓] Labeled CSV saved to: {labeled_csv_path}")
