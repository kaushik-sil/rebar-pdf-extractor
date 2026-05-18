"""Simple extraction pipeline for demo UI and CLI integration."""

from __future__ import annotations

from pathlib import Path

from .export_csv import write_csv
from .ocr import ocr_image, tesseract_available
from .parser import ExtractedItem, parse_text
from .pdf_reader import extract_pages


def run_extraction_pipeline(
    pdf_path: Path,
    output_csv: Path,
    use_ocr: bool = True,
    work_dir: Path | None = None,
) -> dict[str, object]:
    if work_dir is None:
        work_dir = output_csv.parent / "_work" / "pipeline"
    work_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        return {
            "success": False,
            "page_count": 0,
            "rows": 0,
            "output_csv": str(output_csv),
            "warnings": [f"PDF not found: {pdf_path}"],
            "pipeline": {},
        }

    pages = extract_pages(pdf_path, work_dir / "pages")
    ocr_ok = use_ocr and tesseract_available()
    warnings: list[str] = []
    if use_ocr and not ocr_ok:
        warnings.append("Tesseract not found; OCR disabled.")

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

    write_csv(all_items, output_csv)

    return {
        "success": True,
        "page_count": len(pages),
        "rows": len(all_items),
        "output_csv": str(output_csv),
        "warnings": warnings,
        "pipeline": {
            "pdf_loaded": True,
            "text_extracted": True,
            "ocr_enabled": ocr_ok,
            "parsed": True,
            "exported": True,
        },
    }
