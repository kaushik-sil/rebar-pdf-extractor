"""OCR page images with Tesseract (optional if not installed)."""

from __future__ import annotations

from pathlib import Path

import cv2
import pytesseract

_WINDOWS_TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")


def _configure_tesseract() -> None:
    try:
        pytesseract.get_tesseract_version()
        return
    except pytesseract.TesseractNotFoundError:
        pass
    if _WINDOWS_TESSERACT.is_file():
        pytesseract.pytesseract.tesseract_cmd = str(_WINDOWS_TESSERACT)


_configure_tesseract()


def _preprocess(image_path: Path):
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return img


def ocr_image(image_path: Path) -> str:
    processed = _preprocess(image_path)
    if processed is None:
        return ""
    config = "--psm 6 -c preserve_interword_spaces=1"
    return pytesseract.image_to_string(processed, config=config).strip()


def tesseract_available() -> bool:
    try:
        pytesseract.get_tesseract_version()
        return True
    except pytesseract.TesseractNotFoundError:
        return False
