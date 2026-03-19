from __future__ import annotations

from pathlib import Path
import sqlite3
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRANSFORM_DIR = PROJECT_ROOT / "transform" / "data"
DB_DIR = PROJECT_ROOT / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "precious_metal.db"


def load_csv_to_sql(table_name: str, csv_path: Path) -> int:
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    with sqlite3.connect(DB_PATH) as conn:
        # Use the stdlib SQLite driver to avoid an unnecessary SQLAlchemy dependency.
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    return len(df)


def main() -> None:
    mapping = {
        "gold_futures_features": TRANSFORM_DIR / "gold_futures_features.csv",
        "silver_futures_features": TRANSFORM_DIR / "silver_futures_features.csv",
    }

    for table, path in mapping.items():
        n = load_csv_to_sql(table, path)
        print(f"Loaded {n} rows into table: {table}")

    print(f"SQLite DB saved at: {DB_PATH}")


if __name__ == "__main__":
    main()
