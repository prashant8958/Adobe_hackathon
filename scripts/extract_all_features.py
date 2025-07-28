import os
import sys
import pandas as pd

# 👇 Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pdf_utils import extract_text_elements

INPUT_DIR = "data/input"
OUTPUT_DIR = "data/features"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_features_from_pdf(pdf_path, output_csv):
    try:
        elements = extract_text_elements(pdf_path)
        rows = []

        for elem in elements:
            text = elem["text"].strip()
            if not text:
                continue
            font_size = elem["font_size"]
            font_name = elem["font_name"]
            is_bold = int("Bold" in font_name or "bold" in font_name)
            is_title_case = int(text.istitle())
            is_uppercase = int(text.isupper())
            x = elem["x"]
            y = elem["y"]
            page = elem["page"]
            line_len = len(text)

            rows.append({
                "text": text,
                "font_size": font_size,
                "font_name": font_name,
                "is_bold": is_bold,
                "is_title_case": is_title_case,
                "is_uppercase": is_uppercase,
                "x": x,
                "y": y,
                "page": page,
                "line_len": line_len,
            })

        df = pd.DataFrame(rows)
        df.to_csv(output_csv, index=False)
        print(f"[✓] {os.path.basename(pdf_path)} → {os.path.basename(output_csv)}")

    except Exception as e:
        print(f"[✗] Failed to process {pdf_path}: {e}")

def main():
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(INPUT_DIR, filename)
            output_csv = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".csv"))
            extract_features_from_pdf(input_path, output_csv)

if __name__ == "__main__":
    main()
