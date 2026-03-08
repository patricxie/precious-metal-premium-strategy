import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def build_equity_curve(trades_df, initial_capital=10000):
    """
    根據每筆交易報酬率，計算累積資金曲線
    """
    trades_df = trades_df.sort_values("date").copy()
    capital = initial_capital
    capitals = []

    for _, row in trades_df.iterrows():
        r = row["forward_return_pct"] / 100
        capital = capital * (1 + r)
        capitals.append(capital)

    trades_df["equity"] = capitals
    return trades_df


def run_equity_curve():
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "data" / "processed" / "recent_2year_signal_backtest.csv"
    output_dir = base_dir / "data" / "processed" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"找不到檔案：{input_path}")

    df = pd.read_csv(input_path)
    df["date"] = pd.to_datetime(df["date"])

    # 只先看表現最好的兩個策略
    gold_buy_20 = df[
        (df["asset"] == "gold") &
        (df["signal"] == "BUY") &
        (df["holding_days"] == 20)
    ].copy()

    silver_buy_20 = df[
        (df["asset"] == "silver") &
        (df["signal"] == "BUY") &
        (df["holding_days"] == 20)
    ].copy()

    if gold_buy_20.empty:
        print("沒有 Gold BUY 20D 可畫圖。")
    else:
        gold_curve = build_equity_curve(gold_buy_20, initial_capital=10000)

        plt.figure(figsize=(12, 6))
        plt.plot(gold_curve["date"], gold_curve["equity"])
        plt.title("Equity Curve - Gold BUY 20D")
        plt.xlabel("Date")
        plt.ylabel("Capital")
        plt.tight_layout()

        output_path = output_dir / "equity_curve_gold_buy_20d.png"
        plt.savefig(output_path, dpi=150)
        plt.close()

        print(f"已儲存：{output_path}")
        print("\nGold BUY 20D 最後資金：")
        print(round(gold_curve['equity'].iloc[-1], 2))

    if silver_buy_20.empty:
        print("沒有 Silver BUY 20D 可畫圖。")
    else:
        silver_curve = build_equity_curve(silver_buy_20, initial_capital=10000)

        plt.figure(figsize=(12, 6))
        plt.plot(silver_curve["date"], silver_curve["equity"])
        plt.title("Equity Curve - Silver BUY 20D")
        plt.xlabel("Date")
        plt.ylabel("Capital")
        plt.tight_layout()

        output_path = output_dir / "equity_curve_silver_buy_20d.png"
        plt.savefig(output_path, dpi=150)
        plt.close()

        print(f"已儲存：{output_path}")
        print("\nSilver BUY 20D 最後資金：")
        print(round(silver_curve['equity'].iloc[-1], 2))


if __name__ == "__main__":
    run_equity_curve()