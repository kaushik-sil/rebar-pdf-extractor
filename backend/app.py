from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src.export_csv import write_csv
from src.ocr import ocr_image, tesseract_available
from src.parser import ExtractedItem, parse_text
from src.pdf_reader import extract_pages

app = FastAPI(title="Rebar PDF Extractor API")


class ExtractRequest(BaseModel):
    pdf_path: str
    output_csv: Optional[str] = "output/extracted.csv"
    use_ocr: bool = True


class ExtractResult(BaseModel):
    success: bool
    page_count: int
    rows: int
    output_csv: str
    warnings: List[str] = []


@app.get("/")
def root():
    return {"message": "Rebar PDF Extractor API is running."}


@app.post("/extract", response_model=ExtractResult)
def extract(request: ExtractRequest):
    pdf_path = Path(request.pdf_path)
    output_csv = Path(request.output_csv)
    warnings: List[str] = []

    if not pdf_path.exists():
        return {
            "success": False,
            "page_count": 0,
            "rows": 0,
            "output_csv": str(output_csv),
            "warnings": [f"PDF not found: {pdf_path}"],
        }

    work_dir = Path("output") / "_work" / "api_pages"
    work_dir.mkdir(parents=True, exist_ok=True)

    pages = extract_pages(pdf_path, work_dir)
    ocr_ok = request.use_ocr and tesseract_available()
    if request.use_ocr and not ocr_ok:
        warnings.append("Tesseract not available; using PDF text layer only.")

    all_items: List[ExtractedItem] = []
    for page in pages:
        combined = page.text_layer
        sources = ["pdf_text"]
        if ocr_ok and page.image_path:
            ocr_text = ocr_image(page.image_path)
            if ocr_text:
                combined = f"{combined}\n{ocr_text}".strip()
                sources.append("ocr")

        items = parse_text(combined, page.page_number, "+".join(sources))
        all_items.extend(items)

    write_csv(all_items, output_csv)

    return {
        "success": True,
        "page_count": len(pages),
        "rows": len(all_items),
        "output_csv": str(output_csv),
        "warnings": warnings,
    }
