import os
import sys
import argparse
import pandas as pd
# from utils.pdf_utils import extract_text_elements
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pdf_utils import extract_text_elements
# import pandas as pd


def extract_features(input_pdf, output_csv):
    elements = extract_text_elements(input_pdf)

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
    print(f"[✓] Saved extracted features → {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_pdf", required=True, help="Path to input PDF")
    parser.add_argument("--output_csv", required=True, help="Path to output CSV")

    args = parser.parse_args()
    extract_features(args.input_pdf, args.output_csv)
