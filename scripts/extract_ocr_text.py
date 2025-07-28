from pdf2image import convert_from_path
import pytesseract
import os

pdf_path = "data/input/p7_adobe.pdf"
output_txt = "data/output/p7_ocr.txt"

print(f"[•] Processing: {pdf_path}")

try:
    images = convert_from_path(pdf_path, dpi=150)

    full_text = ""
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image)
        full_text += f"\n\n--- Page {i+1} ---\n{text}"

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"[✓] OCR text saved to: {output_txt}")

except Exception as e:
    print(f"[✗] Failed: {e}")
