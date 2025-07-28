import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

def extract_text_elements(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_elements = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        text_found = False

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    text_found = True
                    extracted_elements.append({
                        "text": text,
                        "font_size": span["size"],
                        "font_name": span["font"],
                        "x": span["bbox"][0],
                        "y": span["bbox"][1],
                        "page": page_num + 1,
                    })

        # 👇 Fallback to OCR if no text found on this page
        if not text_found:
            print(f"[OCR] Page {page_num+1} has no extractable text, using OCR...")
            images = convert_from_path(pdf_path, dpi=150, first_page=page_num+1, last_page=page_num+1)
            if images:
                ocr_data = pytesseract.image_to_data(images[0], output_type=pytesseract.Output.DICT)
                num_boxes = len(ocr_data['text'])
                for i in range(num_boxes):
                    text = ocr_data['text'][i].strip()
                    if not text:
                        continue
                    extracted_elements.append({
                        "text": text,
                        "font_size": 12,  # placeholder
                        "font_name": "OCR",
                        "x": ocr_data['left'][i],
                        "y": ocr_data['top'][i],
                        "page": page_num + 1,
                    })

    return extracted_elements
