# Adobe_project 
# Intelligent PDF Outline Extractor – Hackathon Submission

## Problem Statement
Building a fast, accurate, and offline system that extracts **structured outlines (Title, H1–H3)** from complex PDF documents – including scanned or image-based PDFs – to enable better document navigation and personalized information retrieval.

---

##  Features

- Extracts structured outline: **Title, H1, H2, H3**
- Handles scanned/image-based PDFs using **EasyOCR**
- Supports **multilingual** text extraction + optional **translation to English**
- Uses **ML-based classification** (Random Forest) to improve heading accuracy
- Filters out:
  - Section titles with bullets (•,  7, etc.)
  - Generic or short (< 5 words) titles
-  Fully offline, **CPU-only**
-  < 1GB total size
-  Processes PDF in **≤ 60 seconds**
-  Dockerized: Easy to run anywhere

## Tech Stack

-- Python, PyMuPDF, EasyOCR, scikit-learn, langdetect

-- Docker

-- Open-source & offline-friendly
