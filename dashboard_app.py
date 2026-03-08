import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from pathlib import Path


# =========================
# 基本設定
# =========================
st.set_page_config(
    page_title="Precious Metal Strategy Dashboard",
    layout="wide"
)

base_dir = Path(__file__).resolve().parent
processed_dir = base_dir / "data" / "processed"

premium_path = processed_dir / "premium_analysis.csv"
backtest_path = processed_dir / "recent_2year_signal_backtest.csv"
risk_path = processed_dir / "recent_2year_risk_metrics.csv"
summary_path = processed_dir / "recent_2year_backtest_report_table.csv"


# =========================
# 讀取資料
# =========================
@st.cache_data
def load_data():
    if not premium_path.exists():
        raise FileNotFoundError(f"找不到檔案：{premium_path}")
    if not backtest_path.exists():
        raise FileNotFoundError(f"找不到檔案：{backtest_path}")
    if not risk_path.exists():
        raise FileNotFoundError(f"找不到檔案：{risk_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"找不到檔案：{summary_path}")

    premium_df = pd.read_csv(premium_path)
    backtest_df = pd.read_csv(backtest_path)
    risk_df = pd.read_csv(risk_path)
    summary_df = pd.read_csv(summary_path)

    premium_df["date"] = pd.to_datetime(premium_df["date"])
    backtest_df["date"] = pd.to_datetime(backtest_df["date"])

    return premium_df, backtest_df, risk_df, summary_df


premium_df, backtest_df, risk_df, summary_df = load_data()


# =========================
# 工具函式
# =========================
def build_equity_curve(trades_df, initial_capital=10000):
    trades_df = trades_df.sort_values("date").copy()
    capital = initial_capital
    equities = []

    for _, row in trades_df.iterrows():
        r = row["forward_return_pct"] / 100.0
        capital = capital * (1 + r)
        equities.append(capital)

    trades_df["equity"] = equities
    return trades_df


def get_signal_col(asset):
    return "gold_signal_z" if asset == "gold" else "silver_signal_z"


def get_zscore_col(asset):
    return "gold_zscore" if asset == "gold" else "silver_zscore"


# =========================
# 標題
# =========================
st.title("Precious Metal Strategy Dashboard")
st.markdown("黃金 / 白銀 期貨-現貨溢價率、Z-score 訊號、回測與風險指標")

# =========================
# 側邊欄篩選
# =========================
st.sidebar.header("篩選條件")

asset = st.sidebar.selectbox("資產", ["gold", "silver"])
signal = st.sidebar.selectbox("訊號", ["BUY", "SELL"])
holding_days = st.sidebar.selectbox("持有天數", [5, 10, 20])

selected_backtest = backtest_df[
    (backtest_df["asset"] == asset) &
    (backtest_df["signal"] == signal) &
    (backtest_df["holding_days"] == holding_days)
].copy()

selected_risk = risk_df[
    (risk_df["asset"] == asset) &
    (risk_df["signal"] == signal) &
    (risk_df["holding_days"] == holding_days)
].copy()

selected_summary = summary_df[
    (summary_df["asset"] == asset) &
    (summary_df["signal"] == signal) &
    (summary_df["holding_days"] == holding_days)
].copy()

# 最近 2 年 premium / zscore 資料
latest_date = premium_df["date"].max()
start_date = latest_date - pd.Timedelta(days=730)
recent_2y = premium_df[premium_df["date"] >= start_date].copy()

signal_col = get_signal_col(asset)
zscore_col = get_zscore_col(asset)

buy_points = recent_2y[recent_2y[signal_col] == "BUY"]
sell_points = recent_2y[recent_2y[signal_col] == "SELL"]


# =========================
# KPI 區
# =========================
st.subheader("策略摘要")

if not selected_risk.empty:
    row = selected_risk.iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Final Capital", f"{row['final_capital']:.2f}")
    col2.metric("Total Return (%)", f"{row['total_return_pct']:.2f}")
    col3.metric("Win Rate (%)", f"{row['win_rate_pct']:.2f}")
    col4.metric("Max Drawdown (%)", f"{row['max_drawdown_pct']:.2f}")
    col5.metric("Sharpe Ratio", f"{row['sharpe_ratio']:.4f}")
else:
    st.warning("目前選擇的策略沒有風險指標資料。")


# =========================
# 風險指標表
# =========================
st.subheader("風險指標表")
if not selected_risk.empty:
    st.dataframe(selected_risk, use_container_width=True)
else:
    st.info("沒有對應的風險指標資料。")


# =========================
# 資金曲線
# =========================
st.subheader("資金曲線")

if not selected_backtest.empty:
    equity_df = build_equity_curve(selected_backtest, initial_capital=10000)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(equity_df["date"], equity_df["equity"])
    ax.set_title(f"Equity Curve - {asset.upper()} {signal} {holding_days}D")
    ax.set_xlabel("Date")
    ax.set_ylabel("Capital")
    st.pyplot(fig)
else:
    st.info("這個策略沒有回測資料可畫資金曲線。")


# =========================
# Z-score 訊號圖
# =========================
st.subheader("Z-score 訊號圖（最近 2 年）")

fig2, ax2 = plt.subplots(figsize=(14, 5))
ax2.plot(recent_2y["date"], recent_2y[zscore_col], label=f"{asset.upper()} Z-score")
ax2.axhline(2, linestyle="--", label="SELL Threshold (+2)")
ax2.axhline(-2, linestyle="--", label="BUY Threshold (-2)")
ax2.axhline(0, linestyle=":")

ax2.scatter(
    buy_points["date"],
    buy_points[zscore_col],
    marker="^",
    s=70,
    label="BUY"
)
ax2.scatter(
    sell_points["date"],
    sell_points[zscore_col],
    marker="v",
    s=70,
    label="SELL"
)

ax2.set_title(f"{asset.upper()} Z-score with BUY / SELL Signals")
ax2.set_xlabel("Date")
ax2.set_ylabel("Z-score")
ax2.legend()
st.pyplot(fig2)


# =========================
# 回測明細
# =========================
st.subheader("回測明細")
if not selected_backtest.empty:
    st.dataframe(selected_backtest, use_container_width=True)
else:
    st.info("這個策略沒有回測明細資料。")


# =========================
# 全部策略排名
# =========================
st.subheader("全部策略排名（依平均報酬）")
ranking_df = summary_df.sort_values("avg_return_pct", ascending=False).reset_index(drop=True)
st.dataframe(ranking_df, use_container_width=True)