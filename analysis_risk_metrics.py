import pandas as pd
import numpy as np
from pathlib import Path


def build_equity_curve(trades_df, initial_capital=10000):
    trades_df = trades_df.sort_values("date").copy()
    capital = initial_capital
    equities = [capital]
    returns = []

    for _, row in trades_df.iterrows():
        r = row["forward_return_pct"] / 100.0
        capital = capital * (1 + r)
        equities.append(capital)
        returns.append(r)

    curve_df = trades_df.copy().reset_index(drop=True)
    curve_df["trade_return"] = returns
    curve_df["equity"] = equities[1:]

    return curve_df


def calculate_max_drawdown(equity_series):
    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    return max_drawdown * 100


def calculate_volatility(return_series):
    if len(return_series) <= 1:
        return np.nan
    return return_series.std(ddof=1) * 100


def calculate_sharpe_ratio(return_series):
    if len(return_series) <= 1:
        return np.nan

    std = return_series.std(ddof=1)
    if std == 0:
        return np.nan

    sharpe = return_series.mean() / std
    return sharpe


def analyze_strategy(df, asset, signal, holding_days, initial_capital=10000):
    trades = df[
        (df["asset"] == asset) &
        (df["signal"] == signal) &
        (df["holding_days"] == holding_days)
    ].copy()

    if trades.empty:
        return None

    curve_df = build_equity_curve(trades, initial_capital=initial_capital)

    final_capital = curve_df["equity"].iloc[-1]
    total_return_pct = (final_capital / initial_capital - 1) * 100
    max_drawdown_pct = calculate_max_drawdown(curve_df["equity"])
    volatility_pct = calculate_volatility(curve_df["trade_return"])
    sharpe_ratio = calculate_sharpe_ratio(curve_df["trade_return"])
    win_rate_pct = (curve_df["trade_return"] > 0).mean() * 100

    return {
        "asset": asset,
        "signal": signal,
        "holding_days": holding_days,
        "trades": len(curve_df),
        "final_capital": round(final_capital, 2),
        "total_return_pct": round(total_return_pct, 2),
        "win_rate_pct": round(win_rate_pct, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "volatility_pct": round(volatility_pct, 2) if pd.notna(volatility_pct) else np.nan,
        "sharpe_ratio": round(sharpe_ratio, 4) if pd.notna(sharpe_ratio) else np.nan,
    }


def run_risk_metrics():
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "data" / "processed" / "recent_2year_signal_backtest.csv"
    output_path = base_dir / "data" / "processed" / "recent_2year_risk_metrics.csv"

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

    results = []
    for asset, signal, holding_days in strategies:
        result = analyze_strategy(df, asset, signal, holding_days)
        if result is not None:
            results.append(result)

    result_df = pd.DataFrame(results)

    if result_df.empty:
        print("沒有可分析的策略資料。")
        return

    result_df = result_df.sort_values(
        by=["total_return_pct", "sharpe_ratio"],
        ascending=[False, False]
    ).reset_index(drop=True)

    result_df.to_csv(output_path, index=False)

    print("風險指標結果已儲存到：")
    print(output_path)

    print("\n風險指標總表：")
    print(result_df)


if __name__ == "__main__":
    run_risk_metrics()