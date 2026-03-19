from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
EXTRACT_DIR = PROJECT_ROOT / "extract" / "data"
TRANSFORM_DIR = PROJECT_ROOT / "transform" / "data"
DB_PATH = PROJECT_ROOT / "database" / "precious_metal.db"


def assert_file_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")


def resolve_columns(df: pd.DataFrame, expected_cols: list[str]) -> list[str]:
    resolved: list[str] = []
    normalized = {col.lower().replace(" ", "").replace("_", ""): col for col in df.columns}

    for expected in expected_cols:
        key = expected.lower().replace(" ", "").replace("_", "")
        if key in normalized:
            resolved.append(normalized[key])
            continue

        if expected == "close":
            close_candidates = [col for col in df.columns if "close" in col.lower() and "adj" not in col.lower()]
            if close_candidates:
                resolved.append(close_candidates[0])
                continue

        raise KeyError(f"{df.columns.tolist()} does not contain a match for: {expected}")

    return resolved


def check_csv(
    path: Path,
    date_col: str,
    required_cols: list[str],
    non_null_cols: list[str],
) -> None:
    assert_file_exists(path)
    df = pd.read_csv(path)

    resolved_required_cols = resolve_columns(df, required_cols)
    resolved_non_null_cols = resolve_columns(df, non_null_cols)
    resolved_date_col = resolve_columns(df, [date_col])[0]

    if df.empty:
        raise ValueError(f"{path.name} is empty")

    if df[resolved_non_null_cols].isna().any().any():
        na_cols = df[resolved_non_null_cols].columns[df[resolved_non_null_cols].isna().any()].tolist()
        raise ValueError(f"{path.name} has nulls in required columns: {na_cols}")

    parsed_dates = pd.to_datetime(df[resolved_date_col], errors="coerce")
    if parsed_dates.isna().any():
        raise ValueError(f"{path.name} contains invalid dates in column: {resolved_date_col}")

    if parsed_dates.duplicated().any():
        raise ValueError(f"{path.name} contains duplicate dates")

    latest_row = df.loc[parsed_dates.idxmax(), resolved_required_cols]
    if latest_row.isna().any():
        raise ValueError(f"{path.name} latest row has nulls: {latest_row[latest_row.isna()].index.tolist()}")

    print(
        f"OK CSV: {path.name} | rows={len(df)} | "
        f"latest_date={parsed_dates.max().date()}"
    )


def check_sqlite_table(table_name: str) -> None:
    assert_file_exists(DB_PATH)
    with sqlite3.connect(DB_PATH) as conn:
        count = pd.read_sql_query(f"SELECT COUNT(*) AS count FROM {table_name}", conn).iloc[0]["count"]
        latest = pd.read_sql_query(f'SELECT MAX("Date") AS latest_date FROM {table_name}', conn).iloc[0]["latest_date"]

    if int(count) <= 0:
        raise ValueError(f"SQLite table {table_name} is empty")

    print(f"OK DB: {table_name} | rows={count} | latest_date={latest}")


def main() -> None:
    csv_checks = [
        (
            EXTRACT_DIR / "gold_futures.csv",
            "Date",
            ["Date", "close"],
            ["Date", "close"],
        ),
        (
            EXTRACT_DIR / "silver_futures.csv",
            "Date",
            ["Date", "close"],
            ["Date", "close"],
        ),
        (
            TRANSFORM_DIR / "gold_futures_features.csv",
            "Date",
            ["Date", "close", "ma_20", "ma_60", "dev_ma20_z", "signal"],
            ["Date", "close", "signal"],
        ),
        (
            TRANSFORM_DIR / "silver_futures_features.csv",
            "Date",
            ["Date", "close", "ma_20", "ma_60", "dev_ma20_z", "signal"],
            ["Date", "close", "signal"],
        ),
    ]

    for path, date_col, required_cols, non_null_cols in csv_checks:
        check_csv(path, date_col, required_cols, non_null_cols)

    for table_name in ["gold_futures_features", "silver_futures_features"]:
        check_sqlite_table(table_name)

    print("Pipeline health check passed.")


if __name__ == "__main__":
    main()
