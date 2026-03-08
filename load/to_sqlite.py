from __future__ import annotations

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRANSFORM_DIR = PROJECT_ROOT / "transform" / "data"
DB_DIR = PROJECT_ROOT / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "precious_metal.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}")


def load_csv_to_sql(table_name: str, csv_path: Path) -> int:
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    # SQLite 裡用 date 欄位存，避免 index 問題
    df.to_sql(table_name, ENGINE, if_exists="replace", index=False)
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

