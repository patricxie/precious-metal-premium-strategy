import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def plot_avg_return(summary_df, output_dir):
    plot_df = summary_df.copy()
    plot_df["label"] = (
        plot_df["holding_days"].astype(str) + "D_" + plot_df["signal"]
    )

    pivot_df = plot_df.pivot_table(
        index="label",
        columns="asset",
        values="avg_return_pct"
    )

    ax = pivot_df.plot(kind="bar", figsize=(12, 6))
    ax.set_title("2-Year Backtest Average Return")
    ax.set_xlabel("Holding Days / Signal")
    ax.set_ylabel("Average Return (%)")
    ax.legend(title="Asset")
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path = output_dir / "backtest_avg_return.png"
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"已儲存：{output_path}")


def plot_win_rate(summary_df, output_dir):
    plot_df = summary_df.copy()
    plot_df["label"] = (
        plot_df["holding_days"].astype(str) + "D_" + plot_df["signal"]
    )

    pivot_df = plot_df.pivot_table(
        index="label",
        columns="asset",
        values="win_rate"
    )

    ax = pivot_df.plot(kind="bar", figsize=(12, 6))
    ax.set_title("2-Year Backtest Win Rate")
    ax.set_xlabel("Holding Days / Signal")
    ax.set_ylabel("Win Rate (%)")
    ax.legend(title="Asset")
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path = output_dir / "backtest_win_rate.png"
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"已儲存：{output_path}")


def run_plot():
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "data" / "processed" / "recent_2year_backtest_summary.csv"
    output_dir = base_dir / "data" / "processed" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"找不到摘要檔案：{input_path}")

    summary_df = pd.read_csv(input_path)

    print("摘要資料前幾筆：")
    print(summary_df.head())

    # 檢查必要欄位
    required_cols = [
        "asset",
        "holding_days",
        "signal",
        "avg_return_pct",
        "win_rate"
    ]
    missing_cols = [col for col in required_cols if col not in summary_df.columns]
    if missing_cols:
        raise ValueError(f"摘要檔缺少欄位：{missing_cols}")

    # 數字格式化，圖表顯示更漂亮
    summary_df["avg_return_pct"] = summary_df["avg_return_pct"].round(2)
    summary_df["win_rate"] = summary_df["win_rate"].round(2)

    plot_avg_return(summary_df, output_dir)
    plot_win_rate(summary_df, output_dir)

    print("\n圖表產生完成！")


if __name__ == "__main__":
    run_plot()