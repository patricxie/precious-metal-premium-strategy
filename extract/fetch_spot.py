import pandas as pd
from pathlib import Path


def fetch_spot_data():
    base_dir = Path(__file__).resolve().parent.parent

    gold_path = base_dir / "extract" / "data" / "gold_spot.csv"
    silver_path = base_dir / "extract" / "data" / "silver_spot.csv"

    print("gold spot path:", gold_path)
    print("silver spot path:", silver_path)

    gold = pd.read_csv(gold_path)
    silver = pd.read_csv(silver_path)

    gold.columns = gold.columns.str.strip()
    silver.columns = silver.columns.str.strip()

    print("gold spot columns:", gold.columns.tolist())
    print("silver spot columns:", silver.columns.tolist())

    gold = gold[["date", "gold_spot"]].copy()
    silver = silver[["date", "silver_spot"]].copy()

    gold["date"] = pd.to_datetime(gold["date"])
    silver["date"] = pd.to_datetime(silver["date"])

    df = pd.merge(gold, silver, on="date", how="inner")
    df = df.sort_values("date").reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = fetch_spot_data()
    print(df.head())