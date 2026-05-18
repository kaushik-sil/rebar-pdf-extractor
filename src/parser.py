"""Parse structural-plan style text for symbols, dimensions, and spacing."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ExtractedItem:
    page_number: int
    category: str
    value: str
    source: str
    context: str


# Rebar: #4, 3-#5, #5@12"
REBAR = re.compile(
    r"(?P<qty>\d+\s*-\s*)?#(?P<size>\d+)\s*(?:@\s*(?P<spacing>[\d'\"./\s]+))?",
    re.IGNORECASE,
)

# Spacing: @ 12" o.c., 12" o.c.
SPACING = re.compile(
    r"@\s*([\d'\"./]+)|(\d+\s*[\"']?\s*o\.?\s*c\.?)",
    re.IGNORECASE,
)

# Dimensions: 12'-6", 24", 300mm (not bare N x N — those are section callouts)
DIMENSION = re.compile(
    r"\b(\d+\s*['′]\s*-\s*\d+(?:\s*[\"″]+)?|\d+\s*[\"″]+|\d+\s*mm)\b",
    re.IGNORECASE,
)

# Common steel / section callouts
SYMBOL = re.compile(
    r"\b(W\d+\s*[xX×]\s*\d+|HSS\s*\d+\s*[xX×]\s*\d+|#\d+\s*bar[s]?)\b",
    re.IGNORECASE,
)


def _context(text: str, start: int, end: int, window: int = 40) -> str:
    lo = max(0, start - window)
    hi = min(len(text), end + window)
    snippet = text[lo:hi].replace("\n", " ")
    return " ".join(snippet.split())


def parse_text(text: str, page_number: int, source: str) -> list[ExtractedItem]:
    if not text.strip():
        return []

    items: list[ExtractedItem] = []
    seen: set[tuple[str, str, str]] = set()

    def add(category: str, value: str, start: int, end: int):
        key = (category, value.lower(), source)
        if key in seen:
            return
        seen.add(key)
        items.append(
            ExtractedItem(
                page_number=page_number,
                category=category,
                value=value.strip(),
                source=source,
                context=_context(text, start, end),
            )
        )

    for m in REBAR.finditer(text):
        parts = [f"#{m.group('size')}"]
        if m.group("qty"):
            parts.insert(0, m.group("qty").strip())
        if m.group("spacing"):
            parts.append(f"@ {m.group('spacing').strip()}")
        add("rebar", "".join(parts), m.start(), m.end())

    for m in SPACING.finditer(text):
        val = (m.group(1) or m.group(2) or "").strip()
        if val:
            add("spacing", val if val.startswith("@") else f"@ {val}", m.start(), m.end())

    for m in DIMENSION.finditer(text):
        add("dimension", m.group(1), m.start(), m.end())

    for m in SYMBOL.finditer(text):
        add("symbol", m.group(1), m.start(), m.end())

    return items
