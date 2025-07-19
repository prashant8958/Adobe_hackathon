import fitz  # PyMuPDF
from collections import Counter
import json
import regex as re

PDF_PATH = "Unit.pdf"
OUTPUT_PATH = "output.json"

doc = fitz.open(PDF_PATH)
if doc.page_count > 50:
    raise ValueError("PDF exceeds 50 pages limit")

spans_data = []
images_data = []

# Step 1: Extract text spans and image info
for page_num in range(len(doc)):
    page = doc[page_num]
    blocks = page.get_text("dict")["blocks"]

    # TEXT
    for block in blocks:
        if block["type"] == 0:  # text block
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if text:
                        spans_data.append({
                            "text": text,
                            "size": round(span["size"], 1),
                            "font": span["font"],
                            "page": page_num + 1
                        })

    # IMAGES
    for img in page.get_images(full=True):
        xref = img[0]
        bbox = doc.extract_image(xref)["bbox"] if "bbox" in doc.extract_image(xref) else None
        image_rects = [i["bbox"] for i in page.get_text("dict")["blocks"] if i["type"] == 1]
        for rect in image_rects:
            images_data.append({
                "page": page_num + 1,
                "bbox": rect  # [x0, y0, x1, y1]
            })

# Step 2: Font size frequency analysis
font_sizes = [s["size"] for s in spans_data]
size_counts = Counter(font_sizes)
sorted_sizes = sorted(size_counts.items(), key=lambda x: -x[0])
top_sizes = [s[0] for s in sorted_sizes[:4]]

# Step 3: Map top sizes to Title, H1, H2, H3
font_map = {}
labels = ["Title", "H1", "H2", "H3"]
for i, size in enumerate(top_sizes):
    if i < len(labels):
        font_map[size] = labels[i]

# Step 4: Filter headings
title = None
outline = []

def is_probably_heading(text):
     return (
        len(text) < 100 and
        not re.search(r"[.!؟。]", text.strip()) and  # punctuation from various scripts
        re.search(r"\p{L}", text, re.UNICODE) is not None
    )

for span in spans_data:
    size = span["size"]
    label = font_map.get(size)

    if label and is_probably_heading(span["text"]):
        if label == "Title" and not title:
            title = span["text"]
        elif label != "Title":
            outline.append({
                "level": label,
                "text": span["text"],
                "page": span["page"]
            })

# Step 5: Create final structure
output = {
    "title": title if title else "Unknown Title",
    "outline": outline,
    "images": images_data
}

# Step 6: Save as JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Text & images extracted and saved to '{OUTPUT_PATH}'")
