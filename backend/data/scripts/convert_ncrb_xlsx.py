"""
Converts real NCRB (National Crime Records Bureau, Govt. of India) 'Crime in
India 2023' city-wise XLSX tables — sourced via the Open Government Data
Platform India mirror on data.opencity.in — into flat CSV files usable by the
platform. The source tables use merged, multi-row headers; this script
forward-fills and flattens them into single-row column names without altering
any underlying figures.

Run: python convert_ncrb_xlsx.py
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "raw"
XLSX_DIR = RAW_DIR / "ncrb_xlsx"

# (xlsx filename, output csv filename, number of header rows incl. row 1, has marker row)
FILES = [
    ("ipc_crimes_citywise_2023.xlsx", "ncrb_ipc_crimes_citywise_2023.csv", 3, False),
    ("crimes_against_women_citywise_2023.xlsx", "ncrb_crimes_against_women_citywise_2023.csv", 3, False),
    ("cyber_crimes_disposal_citywise_2023.xlsx", "ncrb_cyber_crimes_disposal_citywise_2023.csv", 5, True),
    ("ndps_seizures_citywise_2023.xlsx", "ncrb_ndps_seizures_citywise_2023.csv", 4, True),
    ("property_stolen_recovered_citywise_2023.xlsx", "ncrb_property_stolen_recovered_citywise_2023.csv", 4, True),
]


def flatten(xlsx_path: Path, header_rows: int, has_marker: bool):
    raw = pd.read_excel(xlsx_path, header=None)
    title = raw.iloc[0, 0]

    headers = raw.iloc[1:header_rows].ffill(axis=1)
    col_names = []
    for col in range(raw.shape[1]):
        parts = []
        for r in range(len(headers)):
            val = headers.iloc[r, col]
            if pd.notna(val):
                s = str(val).strip()
                if s and (not parts or parts[-1] != s):
                    parts.append(s)
        col_names.append(" - ".join(parts) if parts else f"col_{col}")

    data_start = header_rows + (1 if has_marker else 0)
    data = raw.iloc[data_start:].reset_index(drop=True)
    data.columns = col_names
    data = data.dropna(how="all")
    return title, data


def main():
    for xlsx_name, csv_name, header_rows, has_marker in FILES:
        title, df = flatten(XLSX_DIR / xlsx_name, header_rows, has_marker)
        out_path = RAW_DIR / csv_name
        df.to_csv(out_path, index=False)
        print(f"{xlsx_name}: '{title}' -> {out_path.name} ({len(df)} rows, {len(df.columns)} cols)")


if __name__ == "__main__":
    main()
