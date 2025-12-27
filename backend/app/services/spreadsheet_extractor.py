import io
import pandas as pd

def extract_text_from_spreadsheet(file_bytes: bytes, filename: str) -> dict:
    pages = []

    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_bytes))
        text = df.astype(str).apply(lambda r: ", ".join(r), axis=1).str.cat(sep="\n")
        pages.append({"page_number": 1, "text": text, "meta": {"headers": list(df.columns)}})
    else:
        xls = pd.ExcelFile(io.BytesIO(file_bytes))
        for i, sheet in enumerate(xls.sheet_names, start=1):
            df = xls.parse(sheet)
            text = df.astype(str).apply(lambda r: ", ".join(r), axis=1).str.cat(sep="\n")
            pages.append({"page_number": i, "text": text, "meta": {"sheet": sheet}})

    return {"pages": pages, "meta": {"structured": True}}
