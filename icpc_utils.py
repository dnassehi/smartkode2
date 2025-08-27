# icpc_utils.py
# Helper utilities for ICPC-2 RAG

from __future__ import annotations
import csv
import json
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple
import pandas as pd


@dataclass
class ICPCEntry:
    code: str
    title: str
    component_hint: str  # "symptom", "process", or "diagnosis"
    component_guess: int | None  # 1, 2..6, 7 (None if not sure)
    chapter: str  # letter A–Z


def _detect_delimiter(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        sample = f.read(2048)
        try:
            dialect = csv.Sniffer().sniff(sample)
            return dialect.delimiter
        except Exception:
            return ","


def load_icpc_csv(path: str) -> pd.DataFrame:
    """Load and normalize the ICPC-2 CSV (handles ';' delimiter and trailing spaces)."""
    delim = _detect_delimiter(path)
    df = pd.read_csv(path, delimiter=delim, encoding="utf-8", on_bad_lines="skip")
    # Strip whitespace in column names
    df.columns = df.columns.str.strip()
    # Canonical expected columns: "Kode", "Kodetekst"
    # Some files might have "Kodetekst " with trailing space; we stripped above.
    assert "Kode" in df.columns, f"Expected a 'Kode' column. Found: {list(df.columns)}"
    # Find the text column heuristically
    text_col = None
    for cand in ["Kodetekst", "Tekst", "Tittel", "Title"]:
        if cand in df.columns:
            text_col = cand
            break
    if text_col is None:
        # Fallback: second column
        text_col = df.columns[1]
    df = df[["Kode", text_col]].rename(columns={text_col: "Kodetekst"})
    # Drop rows without code/text
    df = df.dropna(subset=["Kode", "Kodetekst"])
    # Normalize whitespace
    df["Kode"] = df["Kode"].astype(str).str.strip()
    df["Kodetekst"] = df["Kodetekst"].astype(str).str.strip()
    # Deduplicate by code keeping the longest title
    df = (df.sort_values(by="Kodetekst", key=lambda s: s.str.len(), ascending=False)
            .drop_duplicates(subset=["Kode"], keep="first"))
    return df.reset_index(drop=True)


def component_from_code(code: str) -> Tuple[str, int | None]:
    """Roughly infer ICPC-2 component group from the numeric suffix.
    Returns (component_hint, component_guess_number_or_None)
    - 01–29: symptoms/complaints -> component 1
    - 70–99: diagnoses -> component 7
    - 30–69: process codes (2–6). We try a best-effort mapping by decade:
        30–39 -> 2 (diagnostic/screening/preventive)
        40–49 -> 4 (test results / administrative results, varies by locale)
        50–59 -> 3 (treatment/procedures/medication)
        60–69 -> 5 (administrative/referral/other). Some locales may use 6 here as well.
    NOTE: National adaptations may vary; use title text to decide precisely.
    """
    try:
        n = int(code[1:])
    except Exception:
        return "unknown", None
    if 1 <= n <= 29:
        return "symptom", 1
    if 70 <= n <= 99:
        return "diagnosis", 7
    if 30 <= n <= 69:
        if 30 <= n <= 39:
            return "process", 2
        if 40 <= n <= 49:
            return "process", 4
        if 50 <= n <= 59:
            return "process", 3
        if 60 <= n <= 69:
            return "process", 5
        # Fallback for edge cases
        return "process", 2
    return "unknown", None


def to_entries(df: pd.DataFrame) -> List[ICPCEntry]:
    rows: List[ICPCEntry] = []
    for _, r in df.iterrows():
        code = str(r["Kode"]).strip()
        title = str(r["Kodetekst"]).strip()
        hint, comp = component_from_code(code)
        chapter = code[0] if code else "?"
        rows.append(ICPCEntry(code=code, title=title, component_hint=hint, component_guess=comp, chapter=chapter))
    return rows


def build_doc_text(entry: ICPCEntry) -> str:
    """Text used for document embeddings (passage text). Keep compact to save tokens."""
    comp = entry.component_guess if entry.component_guess is not None else ""
    return f"{entry.code} | {entry.title} | component:{comp or entry.component_hint} | chapter:{entry.chapter}"


def save_meta(entries: List[ICPCEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([e.__dict__ for e in entries], f, ensure_ascii=False, indent=2)
