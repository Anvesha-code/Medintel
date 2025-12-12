# app/services/spreadsheet_extractor.py
import io
from typing import Dict, List
import pandas as pd

def _sheet_to_text(df: pd.DataFrame, max_rows: int = None) -> str:
    """
    Convert a DataFrame to a readable textual block.
    Each row becomes: "Col1=val1, Col2=val2, ..."
    """
    lines = []
    cols = list(df.columns)
    for idx, row in df.iterrows():
        cells = []
        for c in cols:
            val = row[c]
            cells.append(f"{c}={val}")
        lines.append(", ".join(cells))
        if max_rows and len(lines) >= max_rows:
            break
    return "\n".join(lines)

def extract_text_from_spreadsheet(file_bytes: bytes, filename: str = None) -> Dict:
    pages = []
    meta = {}
    # decide CSV vs excel by extension in filename
    ext = filename.split(".")[-1].lower() if filename and "." in filename else ""
    try:
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
            text = _sheet_to_text(df, max_rows=500)
            pages.append({"page_number": 1, "text": text, "meta": {"sheet_name": "csv"}})
            meta["sheets"] = 1
        else:
            # Excel
            xls = pd.ExcelFile(io.BytesIO(file_bytes))
            for i, sheet_name in enumerate(xls.sheet_names, start=1):
                df = xls.parse(sheet_name)
                text = _sheet_to_text(df, max_rows=1000)
                pages.append({"page_number": i, "text": text, "meta": {"sheet_name": sheet_name}})
            meta["sheets"] = len(xls.sheet_names)
    except Exception as e:
        # fallback: attempt csv read
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
            text = _sheet_to_text(df)
            pages.append({"page_number": 1, "text": text, "meta": {"sheet_name": "csv_fallback"}})
            meta["sheets"] = 1
        except Exception:
            pages.append({"page_number": 1, "text": "", "meta": {"error": str(e)}})
    return {"pages": pages, "meta": meta}
