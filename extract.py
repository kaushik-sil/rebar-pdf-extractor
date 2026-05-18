#!/usr/bin/env python3
"""
Mini POC: PDF -> text/OCR -> parse (rebar, dimensions, spacing) -> CSV.

Usage:
  python extract.py                          # uses input/sample_plan.pdf
  python extract.py path/to/drawing.pdf
  python extract.py drawing.pdf --no-ocr     # text layer only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.export_csv import write_csv
from src.ocr import ocr_image, tesseract_available
from src.parser import ExtractedItem, parse_text
from src.pdf_reader import extract_pages

ROOT = Path(__file__).resolve().parent
DEFAULT_PDF = ROOT / "input" / "sample_plan.pdf"
DEFAULT_OUT = ROOT / "output" / "extracted.csv"
WORK_DIR = ROOT / "output" / "_work"


def run(pdf_path: Path, output_csv: Path, use_ocr: bool) -> int:
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        print("Run: python scripts/create_sample_pdf.py", file=sys.stderr)
        return 1

    print(f"Reading: {pdf_path}")
    pages = extract_pages(pdf_path, WORK_DIR / "pages")
    ocr_ok = use_ocr and tesseract_available()
    if use_ocr and not ocr_ok:
        print("Note: Tesseract not found — using PDF text layer only.")
        print("  Install: https://github.com/tesseract-ocr/tesseract")

    all_items: list[ExtractedItem] = []

    for page in pages:
        combined = page.text_layer
        sources = ["pdf_text"]

        if ocr_ok and page.image_path:
            ocr_text = ocr_image(page.image_path)
            if ocr_text:
                combined = f"{combined}\n{ocr_text}".strip()
                sources.append("ocr")

        source_label = "+".join(sources)
        items = parse_text(combined, page.page_number, source_label)
        all_items.extend(items)
        print(f"  Page {page.page_number}: {len(items)} items ({source_label})")

    write_csv(all_items, output_csv)
    print(f"\nWrote {len(all_items)} rows -> {output_csv}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract plan data from PDF to CSV")
    parser.add_argument("pdf", nargs="?", default=str(DEFAULT_PDF), help="Input PDF path")
    parser.add_argument("-o", "--output", default=str(DEFAULT_OUT), help="Output CSV path")
    parser.add_argument("--no-ocr", action="store_true", help="Skip OCR (text layer only)")
    args = parser.parse_args()

    return run(
        Path(args.pdf),
        Path(args.output),
        use_ocr=not args.no_ocr,
    )


if __name__ == "__main__":
    raise SystemExit(main())
