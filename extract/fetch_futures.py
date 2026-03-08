import pandas as pd
from pathlib import Path


def fetch_futures_data():

    # 找到專案根目錄
    BASE_DIR = Path(__file__).resolve().parent.parent

    gold_path = BASE_DIR / "extract" / "data" / "gold_futures.csv"
    silver_path = BASE_DIR / "extract" / "data" / "silver_futures.csv"

    print("gold_path:", gold_path)
    print("silver_path:", silver_path)

    gold = pd.read_csv(gold_path)
    silver = pd.read_csv(silver_path)

    # 去除欄位空白
    gold.columns = gold.columns.str.strip()
    silver.columns = silver.columns.str.strip()

    print("gold columns:", gold.columns.tolist())
    print("silver columns:", silver.columns.tolist())

    # 只保留需要的欄位
    gold = gold[["Date", "Close_GC=F"]].copy()
    silver = silver[["Date", "Close_SI=F"]].copy()

    # 改欄位名稱
    gold.columns = ["date", "gold_futures"]
    silver.columns = ["date", "silver_futures"]

    # 轉換日期
    gold["date"] = pd.to_datetime(gold["date"])
    silver["date"] = pd.to_datetime(silver["date"])

    # 合併資料
    df = pd.merge(gold, silver, on="date", how="inner")

    # 排序
    df = df.sort_values("date").reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = fetch_futures_data()
    print(df.head())