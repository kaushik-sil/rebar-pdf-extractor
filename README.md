# Document Reader — Mini POC

Small proof-of-concept for **PDF plan parsing**: text extraction, OCR, regex-based parsing, and **CSV export**.

Built for freelance proposals (structural drawings, rebar callouts, dimensions, spacing).

## What it does

| Step | Tool |
|------|------|
| PDF text layer | `pdfplumber` |
| Page images | `PyMuPDF` (fitz) |
| OCR (scanned pages) | Tesseract + OpenCV preprocessing |
| Parsing | Regex: rebar `#4`, spacing `@ 12"`, dimensions `12'-6"` |
| Output | `output/extracted.csv` |

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Optional: install Tesseract for OCR
# https://github.com/UB-Mannheim/tesseract/wiki

python scripts/create_sample_pdf.py
python extract.py
```

Use your own PDF:

```bash
python extract.py path/to/your_plan.pdf -o output/my_plan.csv
```

## Sample output (CSV)

| page | category | value | source | context |
|------|----------|-------|--------|---------|
| 1 | rebar | #5 @ 12" | pdf_text | ... #5 @ 12" o.c. ... |
| 1 | dimension | 24'-0" | pdf_text | Overall: 24'-0" x 18'-6" |
| 1 | symbol | W12x26 | pdf_text | B1: W12x26 |

## Architecture (scalable next steps)

```
PDF → [text layer + page raster] → OCR merge → parser → CSV/Excel
                              ↓
                    (future: CV templates, GPT-4V, PaddleOCR)
```

## Screenshots for Upwork

1. `input/sample_plan.pdf` (or your client sample)
2. Terminal running `python extract.py`
3. `output/extracted.csv` opened in Excel

## Stack

Python · pdfplumber · PyMuPDF · Tesseract · OpenCV · pandas
