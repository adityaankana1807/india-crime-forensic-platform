from pathlib import Path

import pandas as pd

from app.config import DATA_RAW_DIR, DATA_SYNTHETIC_DIR, DATA_UPLOADS_DIR

CATEGORY_DIRS = {
    "raw": DATA_RAW_DIR,
    "synthetic": DATA_SYNTHETIC_DIR,
    "uploaded": DATA_UPLOADS_DIR,
}


def _resolve(name: str) -> tuple[Path, str]:
    for category, directory in CATEGORY_DIRS.items():
        path = directory / name
        if path.exists():
            return path, category
    raise FileNotFoundError(name)


def list_datasets() -> list[dict]:
    datasets = []
    for category, directory in CATEGORY_DIRS.items():
        for path in sorted(directory.glob("*.csv")):
            try:
                df = pd.read_csv(path)
            except Exception:
                continue
            datasets.append({
                "name": path.name,
                "category": category,
                "rows": len(df),
                "columns": list(df.columns),
                "size_bytes": path.stat().st_size,
            })
    return datasets


def get_stats(name: str, preview_rows: int = 10) -> dict:
    path, category = _resolve(name)
    df = pd.read_csv(path)
    null_counts = df.isnull().sum().to_dict()
    preview = df.head(preview_rows).fillna("").to_dict(orient="records")
    return {
        "name": name,
        "category": category,
        "rows": len(df),
        "columns": list(df.columns),
        "null_counts": {k: int(v) for k, v in null_counts.items()},
        "preview": preview,
    }


def get_path(name: str) -> Path:
    path, _ = _resolve(name)
    return path


def save_upload(filename: str, content: bytes) -> dict:
    safe_name = Path(filename).name
    dest = DATA_UPLOADS_DIR / safe_name
    dest.write_bytes(content)
    df = pd.read_csv(dest)
    return {
        "name": safe_name,
        "category": "uploaded",
        "rows": len(df),
        "columns": list(df.columns),
        "size_bytes": dest.stat().st_size,
    }
