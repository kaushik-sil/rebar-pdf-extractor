"""Export parsed items to CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .parser import ExtractedItem


def write_csv(items: list[ExtractedItem], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "page": i.page_number,
            "category": i.category,
            "value": i.value,
            "source": i.source,
            "context": i.context,
        }
        for i in items
    ]
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=["page", "category", "value", "source", "context"])
    df.to_csv(output_path, index=False)
