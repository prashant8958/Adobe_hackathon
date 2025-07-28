import os
import pytesseract
import pandas as pd
from pdf2image import convert_from_path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

INPUT_PDF = "data/input/p7_adobe.pdf"
OUTPUT_CSV = "data/features/p7_adobe.csv"

# Optional: set path to tesseract.exe if not in PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_image(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    rows = []
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        if data['text'][i].strip() != "":
            rows.append({
                "text": data['text'][i].strip(),
                "x": data['left'][i],
                "y": data['top'][i],
                "width": data['width'][i],
                "height": data['height'][i]
            })
    return rows

def main():
    print(f"[•] Converting PDF to images...")
    images = convert_from_path(INPUT_PDF, dpi=150)

    print(f"[•] Performing OCR in parallel...")
    all_results = []
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(ocr_image, images))

    for page_num, page_rows in enumerate(results, start=1):
        for row in page_rows:
            row["page"] = page_num
            all_results.append(row)

    df = pd.DataFrame(all_results)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[✓] Saved OCR results to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
