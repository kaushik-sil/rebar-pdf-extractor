"""Generate a small sample structural-style PDF for the POC demo."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "input" / "sample_plan.pdf"

LINES = [
    "FOUNDATION PLAN - SHEET S-101",
    "",
    "SLAB REINFORCEMENT:",
    "  #5 @ 12\" o.c. (each way)",
    "  3-#4 at perimeter",
    "",
    "DIMENSIONS:",
    "  Overall: 24'-0\" x 18'-6\"",
    "  Wall thickness: 8\"",
    "  Clear span: 12'-6\"",
    "",
    "BEAM SCHEDULE:",
    "  B1: W12x26",
    "  B2: W10x22",
    "",
    "COLUMN:",
    "  C1: HSS 6 x 6 x 1/4",
    "",
    "NOTES:",
    "  All rebar per ACI 318.",
    "  #4 bars min unless noted.",
]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 11)
    y = height - 72
    for line in LINES:
        c.drawString(72, y, line)
        y -= 16
    c.save()
    print(f"Created {OUT}")


if __name__ == "__main__":
    main()
