# Rebar PDF Extractor

AI-powered PDF extraction system for structural rebar plans using Python, OCR, and computer vision.

## What this repo contains

- `extract.py` – CLI prototype for PDF → text/OCR → parsed items → CSV
- `src/` – extraction modules for PDF, OCR, parsing, and CSV export
- `scripts/create_sample_pdf.py` – generates a demo structural-style PDF
- `input/sample_plan.pdf` – included sample PDF
- `output/` – target folder for extracted CSV output
- `ui/` – Streamlit demo UI for pipeline visualization and extraction

## Features

- PDF text layer extraction with `PyMuPDF`
- OCR fallback via Tesseract for scanned pages
- Regex-based parsing for rebar callouts, dimensions, and spacing
- CSV export for extraction results
- Demo UI for pipeline status and extraction

## Tech stack

- Python
- PyMuPDF
- pdfplumber
- Tesseract / OpenCV
- pandas
- Streamlit
- numpy

## Current status

Prototype in progress:

- PDF text extraction working
- OCR fallback supported
- Sample CSV export available
- Streamlit UI demo added with pipeline status and authentication

## Public demo scope

This repository is a public proof-of-concept and portfolio demo, not a production-ready delivery. It shows:

- starter PDF extraction workflow
- OCR integration
- basic parsing and CSV export

Advanced production logic, optimized extraction rules, and client-specific pipelines are kept private.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/create_sample_pdf.py
python extract.py
```

## CLI usage

```bash
python extract.py path/to/your_plan.pdf -o output/my_plan.csv
python extract.py --no-ocr
```

## UI demo

Run the demo UI with:

```bash
streamlit run ui/streamlit_app.py
```

## Architecture

```
PDF → [text layer + page raster] → OCR merge → parser → CSV export
             ↓
      FastAPI backend / future UI
```

## Notes

- `input/sample_plan.pdf` is the included demo file.
- `output/extracted.csv` is ignored by git.
- Add your own project PDFs under `input/` or `sample_pdfs/`.
