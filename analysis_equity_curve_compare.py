import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def build_equity_curve(trades_df, initial_capital=10000):
    trades_df = trades_df.sort_values("date").copy()
    capital = initial_capital
    capitals = []

    for _, row in trades_df.iterrows():
        r = row["forward_return_pct"] / 100
        capital = capital * (1 + r)
        capitals.append(capital)

    trades_df["equity"] = capitals
    return trades_df


def run_equity_curve_compare():
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "data" / "processed" / "recent_2year_signal_backtest.csv"
    output_dir = base_dir / "data" / "processed" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"找不到檔案：{input_path}")

    df = pd.read_csv(input_path)
    df["date"] = pd.to_datetime(df["date"])

    strategies = [
        ("gold", "BUY", 5),
        ("gold", "BUY", 10),
        ("gold", "BUY", 20),
        ("gold", "SELL", 5),
        ("gold", "SELL", 10),
        ("gold", "SELL", 20),
        ("silver", "BUY", 5),
        ("silver", "BUY", 10),
        ("silver", "BUY", 20),
        ("silver", "SELL", 5),
        ("silver", "SELL", 10),
        ("silver", "SELL", 20),
    ]

    plt.figure(figsize=(16, 8))

    final_results = []

    for asset, signal, holding_days in strategies:
        trades = df[
            (df["asset"] == asset) &
            (df["signal"] == signal) &
            (df["holding_days"] == holding_days)
        ].copy()

        if trades.empty:
            print(f"沒有資料：{asset} {signal} {holding_days}D")
            continue

        curve = build_equity_curve(trades, initial_capital=10000)

        label = f"{asset}_{signal}_{holding_days}D"
        plt.plot(curve["date"], curve["equity"], label=label)

        final_results.append({
            "asset": asset,
            "signal": signal,
            "holding_days": holding_days,
            "final_capital": round(curve["equity"].iloc[-1], 2),
            "trades": len(curve),
            "total_return_pct": round((curve["equity"].iloc[-1] / 10000 - 1) * 100, 2)
        })

    plt.title("Equity Curve Comparison (2-Year Backtest)")
    plt.xlabel("Date")
    plt.ylabel("Capital")
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()

    output_path = output_dir / "equity_curve_comparison_all_strategies.png"
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"\n已儲存圖表：{output_path}")

    result_df = pd.DataFrame(final_results)

    if result_df.empty:
        print("沒有可比較的策略資料。")
        return

    result_df = result_df.sort_values("final_capital", ascending=False).reset_index(drop=True)

    result_output = base_dir / "data" / "processed" / "equity_curve_comparison_all_strategies.csv"
    result_df.to_csv(result_output, index=False)

    print(f"比較結果已儲存：{result_output}")
    print("\n策略最終資金比較：")
    print(result_df)

    print("\n各策略排名（由高到低）：")
    for i, row in result_df.iterrows():
        print(
            f"{i+1}. {row['asset']} {row['signal']} {row['holding_days']}D | "
            f"Final Capital={row['final_capital']} | "
            f"Total Return={row['total_return_pct']}% | "
            f"Trades={row['trades']}"
        )


if __name__ == "__main__":
    run_equity_curve_compare()