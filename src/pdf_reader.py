"""Extract text and page images from PDF files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz
import pdfplumber


@dataclass
class PageContent:
    page_number: int
    text_layer: str
    image_path: Path | None


def extract_pages(pdf_path: Path, image_dir: Path, dpi: int = 200) -> list[PageContent]:
    image_dir.mkdir(parents=True, exist_ok=True)
    pages: list[PageContent] = []

    with pdfplumber.open(pdf_path) as pdf:
        plumber_pages = pdf.pages

        doc = fitz.open(pdf_path)
        try:
            for i, fitz_page in enumerate(doc):
                text = (plumber_pages[i].extract_text() or "").strip() if i < len(plumber_pages) else ""
                pix = fitz_page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
                img_path = image_dir / f"page_{i + 1:03d}.png"
                pix.save(str(img_path))
                pages.append(
                    PageContent(
                        page_number=i + 1,
                        text_layer=text,
                        image_path=img_path,
                    )
                )
        finally:
            doc.close()

    return pages
