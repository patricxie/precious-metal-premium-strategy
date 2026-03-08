import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def plot_gold_zscore(df, output_dir):
    recent_2y = df.copy()

    buy_points = recent_2y[recent_2y["gold_signal_z"] == "BUY"]
    sell_points = recent_2y[recent_2y["gold_signal_z"] == "SELL"]

    plt.figure(figsize=(14, 6))
    plt.plot(recent_2y["date"], recent_2y["gold_zscore"], label="Gold Z-score")
    plt.axhline(2, linestyle="--", label="SELL Threshold (+2)")
    plt.axhline(-2, linestyle="--", label="BUY Threshold (-2)")
    plt.axhline(0, linestyle=":")

    plt.scatter(
        buy_points["date"],
        buy_points["gold_zscore"],
        marker="^",
        s=80,
        label="BUY"
    )

    plt.scatter(
        sell_points["date"],
        sell_points["gold_zscore"],
        marker="v",
        s=80,
        label="SELL"
    )

    plt.title("Gold Z-score with BUY / SELL Signals (Last 2 Years)")
    plt.xlabel("Date")
    plt.ylabel("Z-score")
    plt.legend()
    plt.tight_layout()

    output_path = output_dir / "gold_zscore_2year_signal.png"
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"已儲存：{output_path}")


def plot_silver_zscore(df, output_dir):
    recent_2y = df.copy()

    buy_points = recent_2y[recent_2y["silver_signal_z"] == "BUY"]
    sell_points = recent_2y[recent_2y["silver_signal_z"] == "SELL"]

    plt.figure(figsize=(14, 6))
    plt.plot(recent_2y["date"], recent_2y["silver_zscore"], label="Silver Z-score")
    plt.axhline(2, linestyle="--", label="SELL Threshold (+2)")
    plt.axhline(-2, linestyle="--", label="BUY Threshold (-2)")
    plt.axhline(0, linestyle=":")

    plt.scatter(
        buy_points["date"],
        buy_points["silver_zscore"],
        marker="^",
        s=80,
        label="BUY"
    )

    plt.scatter(
        sell_points["date"],
        sell_points["silver_zscore"],
        marker="v",
        s=80,
        label="SELL"
    )

    plt.title("Silver Z-score with BUY / SELL Signals (Last 2 Years)")
    plt.xlabel("Date")
    plt.ylabel("Z-score")
    plt.legend()
    plt.tight_layout()

    output_path = output_dir / "silver_zscore_2year_signal.png"
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"已儲存：{output_path}")


def run_plot():
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "data" / "processed" / "premium_analysis.csv"
    output_dir = base_dir / "data" / "processed" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"找不到檔案：{input_path}")

    df = pd.read_csv(input_path)
    df["date"] = pd.to_datetime(df["date"])

    required_cols = [
        "date",
        "gold_zscore",
        "silver_zscore",
        "gold_signal_z",
        "silver_signal_z"
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"premium_analysis.csv 缺少欄位：{missing_cols}")

    # 只取最近 2 年
    latest_date = df["date"].max()
    start_date = latest_date - pd.Timedelta(days=730)
    recent_2y = df[df["date"] >= start_date].copy()
    recent_2y = recent_2y.sort_values("date").reset_index(drop=True)

    print("最近 2 年資料區間：")
    print(f"start_date = {recent_2y['date'].min().date()}")
    print(f"end_date   = {recent_2y['date'].max().date()}")
    print(f"rows       = {len(recent_2y)}")

    print("\n最近 2 年黃金訊號統計：")
    print(recent_2y["gold_signal_z"].value_counts())

    print("\n最近 2 年白銀訊號統計：")
    print(recent_2y["silver_signal_z"].value_counts())

    plot_gold_zscore(recent_2y, output_dir)
    plot_silver_zscore(recent_2y, output_dir)

    print("\nZ-score 圖表產生完成！")


if __name__ == "__main__":
    run_plot()