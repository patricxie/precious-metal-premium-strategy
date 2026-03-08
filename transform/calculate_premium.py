import pandas as pd
from pathlib import Path


def calculate_premium():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "extract" / "data"

    # === 讀取期貨資料 ===
    gold_futures_path = data_dir / "gold_futures.csv"
    silver_futures_path = data_dir / "silver_futures.csv"

    gold_futures = pd.read_csv(gold_futures_path)
    silver_futures = pd.read_csv(silver_futures_path)

    gold_futures.columns = gold_futures.columns.str.strip()
    silver_futures.columns = silver_futures.columns.str.strip()

    gold_futures = gold_futures[["Date", "Close_GC=F"]].copy()
    silver_futures = silver_futures[["Date", "Close_SI=F"]].copy()

    gold_futures.columns = ["date", "gold_futures"]
    silver_futures.columns = ["date", "silver_futures"]

    gold_futures["date"] = pd.to_datetime(gold_futures["date"])
    silver_futures["date"] = pd.to_datetime(silver_futures["date"])

    futures_df = pd.merge(gold_futures, silver_futures, on="date", how="inner")

    # === 讀取現貨資料 ===
    gold_spot_path = data_dir / "gold_spot.csv"
    silver_spot_path = data_dir / "silver_spot.csv"

    gold_spot = pd.read_csv(gold_spot_path)
    silver_spot = pd.read_csv(silver_spot_path)

    gold_spot.columns = gold_spot.columns.str.strip()
    silver_spot.columns = silver_spot.columns.str.strip()

    gold_spot = gold_spot[["date", "gold_spot"]].copy()
    silver_spot = silver_spot[["date", "silver_spot"]].copy()

    gold_spot["date"] = pd.to_datetime(gold_spot["date"])
    silver_spot["date"] = pd.to_datetime(silver_spot["date"])

    spot_df = pd.merge(gold_spot, silver_spot, on="date", how="inner")

    # === 合併期貨與現貨 ===
    df = pd.merge(futures_df, spot_df, on="date", how="inner")

    # === 清理缺值 ===
    df = df.dropna(subset=[
        "gold_futures", "silver_futures",
        "gold_spot", "silver_spot"
    ]).copy()

    # === 計算溢價率 ===
    df["gold_premium_pct"] = (df["gold_futures"] - df["gold_spot"]) / df["gold_spot"] * 100
    df["silver_premium_pct"] = (df["silver_futures"] - df["silver_spot"]) / df["silver_spot"] * 100

    # === 固定門檻訊號（保留）===
    df["gold_signal"] = "HOLD"
    df.loc[df["gold_premium_pct"] > 1, "gold_signal"] = "SELL"
    df.loc[df["gold_premium_pct"] < -1, "gold_signal"] = "BUY"

    df["silver_signal"] = "HOLD"
    df.loc[df["silver_premium_pct"] > 1, "silver_signal"] = "SELL"
    df.loc[df["silver_premium_pct"] < -1, "silver_signal"] = "BUY"

    # === 20日 rolling Z-score ===
    window = 20

    df["gold_mean_20"] = df["gold_premium_pct"].rolling(window).mean()
    df["gold_std_20"] = df["gold_premium_pct"].rolling(window).std()

    df["silver_mean_20"] = df["silver_premium_pct"].rolling(window).mean()
    df["silver_std_20"] = df["silver_premium_pct"].rolling(window).std()

    df["gold_zscore"] = (df["gold_premium_pct"] - df["gold_mean_20"]) / df["gold_std_20"]
    df["silver_zscore"] = (df["silver_premium_pct"] - df["silver_mean_20"]) / df["silver_std_20"]

    # 避免 std=0 或 NaN 造成問題
    df["gold_zscore"] = df["gold_zscore"].replace([float("inf"), float("-inf")], pd.NA)
    df["silver_zscore"] = df["silver_zscore"].replace([float("inf"), float("-inf")], pd.NA)

    # === Z-score 訊號 ===
    df["gold_signal_z"] = "HOLD"
    df.loc[df["gold_zscore"] > 2, "gold_signal_z"] = "SELL"
    df.loc[df["gold_zscore"] < -2, "gold_signal_z"] = "BUY"

    df["silver_signal_z"] = "HOLD"
    df.loc[df["silver_zscore"] > 2, "silver_signal_z"] = "SELL"
    df.loc[df["silver_zscore"] < -2, "silver_signal_z"] = "BUY"

    df = df.sort_values("date").reset_index(drop=True)

    return df