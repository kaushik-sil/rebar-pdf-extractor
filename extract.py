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

from src.pipeline import run_extraction_pipeline

ROOT = Path(__file__).resolve().parent
DEFAULT_PDF = ROOT / "input" / "sample_plan.pdf"
DEFAULT_OUT = ROOT / "output" / "extracted.csv"


def run(pdf_path: Path, output_csv: Path, use_ocr: bool) -> int:
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        print("Run: python scripts/create_sample_pdf.py", file=sys.stderr)
        return 1

    print(f"Reading: {pdf_path}")
    result = run_extraction_pipeline(pdf_path, output_csv, use_ocr=use_ocr)
    if not result["success"]:
        for warning in result.get("warnings", []):
            print(f"Warning: {warning}", file=sys.stderr)
        return 1

    for warning in result.get("warnings", []):
        print(f"Warning: {warning}")

    print(f"\nPages processed: {result['page_count']}")
    print(f"Rows extracted: {result['rows']}")
    print(f"Wrote {result['rows']} rows -> {output_csv}")
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
