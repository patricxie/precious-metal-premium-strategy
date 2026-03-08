import pandas as pd
from pathlib import Path


def run_summary_table():
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "data" / "processed" / "recent_2year_signal_backtest.csv"
    output_path = base_dir / "data" / "processed" / "recent_2year_backtest_report_table.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"找不到檔案：{input_path}")

    df = pd.read_csv(input_path)

    required_cols = [
        "asset",
        "holding_days",
        "signal",
        "forward_return_pct"
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"回測明細檔缺少欄位：{missing_cols}")

    summary = (
        df.groupby(["asset", "holding_days", "signal"])
        .agg(
            avg_return_pct=("forward_return_pct", "mean"),
            win_rate_pct=("forward_return_pct", lambda x: (x > 0).mean() * 100),
            trades=("forward_return_pct", "count"),
            max_return_pct=("forward_return_pct", "max"),
            min_return_pct=("forward_return_pct", "min"),
        )
        .reset_index()
    )

    # 數字格式化
    summary["avg_return_pct"] = summary["avg_return_pct"].round(2)
    summary["win_rate_pct"] = summary["win_rate_pct"].round(2)
    summary["max_return_pct"] = summary["max_return_pct"].round(2)
    summary["min_return_pct"] = summary["min_return_pct"].round(2)

    # 排序
    asset_order = {"gold": 0, "silver": 1}
    signal_order = {"BUY": 0, "SELL": 1, "HOLD": 2}

    summary["asset_order"] = summary["asset"].map(asset_order)
    summary["signal_order"] = summary["signal"].map(signal_order)

    summary = summary.sort_values(
        by=["asset_order", "holding_days", "signal_order"]
    ).reset_index(drop=True)

    summary = summary.drop(columns=["asset_order", "signal_order"])

    summary.to_csv(output_path, index=False)

    print("回測摘要總表已儲存到：")
    print(output_path)

    print("\n回測摘要總表：")
    print(summary)


if __name__ == "__main__":
    run_summary_table()