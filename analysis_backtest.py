import pandas as pd
from pathlib import Path


def calculate_forward_return(df, price_col, signal_col, days, asset_name):
    """
    根據訊號計算未來 N 天報酬率
    BUY  -> 做多報酬
    SELL -> 做空報酬
    HOLD -> 不計算
    """
    results = []

    df = df.copy().reset_index(drop=True)

    for i in range(len(df) - days):
        signal = df.loc[i, signal_col]

        if signal == "HOLD":
            continue

        today_price = df.loc[i, price_col]
        future_price = df.loc[i + days, price_col]
        date = df.loc[i, "date"]

        if pd.isna(today_price) or pd.isna(future_price):
            continue

        if signal == "BUY":
            forward_return = (future_price - today_price) / today_price * 100
        elif signal == "SELL":
            forward_return = (today_price - future_price) / today_price * 100
        else:
            continue

        results.append({
            "date": date,
            "asset": asset_name,
            "signal": signal,
            "holding_days": days,
            "today_price": today_price,
            "future_price": future_price,
            "forward_return_pct": forward_return
        })

    return pd.DataFrame(results)


def generate_summary(backtest_df):
    """
    產生摘要統計：
    - 平均報酬
    - 勝率
    - 交易筆數
    - 最大報酬
    - 最小報酬
    """
    if backtest_df.empty:
        return pd.DataFrame(columns=[
            "asset", "holding_days", "signal",
            "avg_return_pct", "win_rate", "trades",
            "max_return_pct", "min_return_pct"
        ])

    summary = (
        backtest_df
        .groupby(["asset", "holding_days", "signal"])
        .agg(
            avg_return_pct=("forward_return_pct", "mean"),
            win_rate=("forward_return_pct", lambda x: (x > 0).mean()),
            trades=("forward_return_pct", "count"),
            max_return_pct=("forward_return_pct", "max"),
            min_return_pct=("forward_return_pct", "min")
        )
        .reset_index()
    )

    summary["win_rate"] = summary["win_rate"] * 100
    return summary


def run_backtest():
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "data" / "processed" / "premium_analysis.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"找不到檔案：{input_path}")

    df = pd.read_csv(input_path)
    df["date"] = pd.to_datetime(df["date"])

    # === 只取最近 2 年資料 ===
    latest_date = df["date"].max()
    start_date = latest_date - pd.Timedelta(days=730)

    recent_2y = df[df["date"] >= start_date].copy()
    recent_2y = recent_2y.sort_values("date").reset_index(drop=True)

    print("最近 2 年資料區間：")
    print(f"start_date = {recent_2y['date'].min().date()}")
    print(f"end_date   = {recent_2y['date'].max().date()}")
    print(f"rows       = {len(recent_2y)}")

    print("\n最近 2 年原始訊號資料（前 20 筆）：")
    print(recent_2y[[
        "date",
        "gold_signal_z",
        "silver_signal_z",
        "gold_futures",
        "silver_futures"
    ]].head(20))

    # === 黃金回測 ===
    gold_5 = calculate_forward_return(recent_2y, "gold_futures", "gold_signal_z", 5, "gold")
    gold_10 = calculate_forward_return(recent_2y, "gold_futures", "gold_signal_z", 10, "gold")
    gold_20 = calculate_forward_return(recent_2y, "gold_futures", "gold_signal_z", 20, "gold")

    gold_backtest = pd.concat([gold_5, gold_10, gold_20], ignore_index=True)

    # === 白銀回測 ===
    silver_5 = calculate_forward_return(recent_2y, "silver_futures", "silver_signal_z", 5, "silver")
    silver_10 = calculate_forward_return(recent_2y, "silver_futures", "silver_signal_z", 10, "silver")
    silver_20 = calculate_forward_return(recent_2y, "silver_futures", "silver_signal_z", 20, "silver")

    silver_backtest = pd.concat([silver_5, silver_10, silver_20], ignore_index=True)

    # === 合併回測結果 ===
    all_backtest = pd.concat([gold_backtest, silver_backtest], ignore_index=True)
    all_backtest = all_backtest.sort_values(["asset", "date", "holding_days"]).reset_index(drop=True)

    # === 產生摘要 ===
    summary_df = generate_summary(all_backtest)

    # === 輸出檔案 ===
    output_detail_path = base_dir / "data" / "processed" / "recent_2year_signal_backtest.csv"
    output_summary_path = base_dir / "data" / "processed" / "recent_2year_backtest_summary.csv"

    all_backtest.to_csv(output_detail_path, index=False)
    summary_df.to_csv(output_summary_path, index=False)

    print(f"\n回測明細已儲存到：{output_detail_path}")
    print(f"回測摘要已儲存到：{output_summary_path}")

    if all_backtest.empty:
        print("\n最近 2 年內沒有可回測的 BUY / SELL 訊號。")
        return

    print("\n前 10 筆回測結果：")
    print(all_backtest.head(10))

    print("\n回測摘要：")
    print(summary_df)

    print("\n各資產訊號次數統計：")
    signal_count = (
        all_backtest
        .groupby(["asset", "holding_days", "signal"])
        .size()
        .reset_index(name="count")
    )
    print(signal_count)


if __name__ == "__main__":
    run_backtest()