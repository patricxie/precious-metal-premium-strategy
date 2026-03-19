import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf
from matplotlib.backends.backend_pdf import PdfPages


st.set_page_config(
    page_title="Precious Metal Quant Dashboard",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHARTS_DIR = PROCESSED_DIR / "charts"

PREMIUM_PATH = PROCESSED_DIR / "premium_analysis.csv"
BACKTEST_PATH = PROCESSED_DIR / "recent_2year_signal_backtest.csv"
RISK_PATH = PROCESSED_DIR / "recent_2year_risk_metrics.csv"
SUMMARY_PATH = PROCESSED_DIR / "recent_2year_backtest_report_table.csv"
COMPARE_PATH = PROCESSED_DIR / "equity_curve_comparison_all_strategies.csv"
LAST_UPDATE_PATH = PROCESSED_DIR / "last_update.json"
PDF_OUTPUT_PATH = PROCESSED_DIR / "strategy_report.pdf"


@st.cache_data
def load_data():
    if not PREMIUM_PATH.exists():
        raise FileNotFoundError(f"找不到檔案：{PREMIUM_PATH}")
    if not BACKTEST_PATH.exists():
        raise FileNotFoundError(f"找不到檔案：{BACKTEST_PATH}")
    if not RISK_PATH.exists():
        raise FileNotFoundError(f"找不到檔案：{RISK_PATH}")
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(f"找不到檔案：{SUMMARY_PATH}")
    if not COMPARE_PATH.exists():
        raise FileNotFoundError(f"找不到檔案：{COMPARE_PATH}")

    premium_df = pd.read_csv(PREMIUM_PATH)
    backtest_df = pd.read_csv(BACKTEST_PATH)
    risk_df = pd.read_csv(RISK_PATH)
    summary_df = pd.read_csv(SUMMARY_PATH)
    compare_df = pd.read_csv(COMPARE_PATH)

    premium_df["date"] = pd.to_datetime(premium_df["date"])
    backtest_df["date"] = pd.to_datetime(backtest_df["date"])

    return premium_df, backtest_df, risk_df, summary_df, compare_df


def _safe_last_close(symbol: str):
    try:
        hist = yf.Ticker(symbol).history(period="5d")
        if hist is None or hist.empty or "Close" not in hist.columns:
            return None
        close_series = hist["Close"].dropna()
        if close_series.empty:
            return None
        return float(close_series.iloc[-1])
    except Exception:
        return None


@st.cache_data(ttl=300)
def get_live_prices_from_yf():
    return {
        "gold_futures": _safe_last_close("GC=F"),
        "silver_futures": _safe_last_close("SI=F"),
        "gold_spot_proxy": _safe_last_close("GLD"),
        "silver_spot_proxy": _safe_last_close("SLV"),
    }


def get_market_panel_data(premium_df: pd.DataFrame):
    latest = premium_df.sort_values("date").iloc[-1]
    live_prices = get_live_prices_from_yf()

    gold_futures = live_prices["gold_futures"]
    if gold_futures is None:
        gold_futures = float(latest["gold_futures"])

    silver_futures = live_prices["silver_futures"]
    if silver_futures is None:
        silver_futures = float(latest["silver_futures"])

    gold_spot_proxy = live_prices["gold_spot_proxy"]
    if gold_spot_proxy is None:
        gold_spot_proxy = float(latest["gold_spot"])

    silver_spot_proxy = live_prices["silver_spot_proxy"]
    if silver_spot_proxy is None:
        silver_spot_proxy = float(latest["silver_spot"])

    return {
        "gold_futures": gold_futures,
        "silver_futures": silver_futures,
        "gold_spot_proxy": gold_spot_proxy,
        "silver_spot_proxy": silver_spot_proxy,
    }


def load_last_update():
    if LAST_UPDATE_PATH.exists():
        with open(LAST_UPDATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "last_update_time": "N/A",
        "status": "unknown",
        "message": "尚未執行每日更新"
    }


def build_equity_curve(trades_df, initial_capital=10000):
    trades_df = trades_df.sort_values("date").copy()
    capital = initial_capital
    equities = []

    for _, row in trades_df.iterrows():
        trade_return = row["forward_return_pct"] / 100.0
        capital = capital * (1 + trade_return)
        equities.append(capital)

    trades_df["equity"] = equities
    return trades_df


def get_signal_col(asset):
    return "gold_signal_z" if asset == "gold" else "silver_signal_z"


def get_zscore_col(asset):
    return "gold_zscore" if asset == "gold" else "silver_zscore"


def get_today_signal(premium_df):
    latest = premium_df.sort_values("date").iloc[-1]
    return {
        "gold_signal": latest["gold_signal_z"],
        "silver_signal": latest["silver_signal_z"],
        "gold_z": latest["gold_zscore"],
        "silver_z": latest["silver_zscore"]
    }


def calculate_max_drawdown(equity_series):
    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max
    return drawdown.min() * 100


def calculate_volatility(return_series):
    if len(return_series) <= 1:
        return None
    return return_series.std(ddof=1) * 100


def calculate_sharpe(return_series):
    if len(return_series) <= 1:
        return None
    std = return_series.std(ddof=1)
    if std == 0:
        return None
    return return_series.mean() / std


def build_portfolio_curve(backtest_df, gold_holding_days, silver_holding_days, gold_weight, silver_weight, initial_capital=10000):
    gold_df = backtest_df[
        (backtest_df["asset"] == "gold") &
        (backtest_df["signal"] == "BUY") &
        (backtest_df["holding_days"] == gold_holding_days)
    ][["date", "forward_return_pct"]].copy()

    silver_df = backtest_df[
        (backtest_df["asset"] == "silver") &
        (backtest_df["signal"] == "BUY") &
        (backtest_df["holding_days"] == silver_holding_days)
    ][["date", "forward_return_pct"]].copy()

    gold_df = gold_df.rename(columns={"forward_return_pct": "gold_return"})
    silver_df = silver_df.rename(columns={"forward_return_pct": "silver_return"})

    merged = pd.merge(gold_df, silver_df, on="date", how="outer").sort_values("date").reset_index(drop=True)
    merged["gold_return"] = merged["gold_return"].fillna(0) / 100.0
    merged["silver_return"] = merged["silver_return"].fillna(0) / 100.0

    total_weight = gold_weight + silver_weight
    if total_weight == 0:
        gold_weight = 0.5
        silver_weight = 0.5
    else:
        gold_weight = gold_weight / total_weight
        silver_weight = silver_weight / total_weight

    merged["portfolio_return"] = (
        merged["gold_return"] * gold_weight +
        merged["silver_return"] * silver_weight
    )

    capital = initial_capital
    equities = []
    for r in merged["portfolio_return"]:
        capital = capital * (1 + r)
        equities.append(capital)

    merged["equity"] = equities

    final_capital = merged["equity"].iloc[-1] if not merged.empty else initial_capital
    total_return_pct = (final_capital / initial_capital - 1) * 100 if not merged.empty else 0
    max_drawdown_pct = calculate_max_drawdown(merged["equity"]) if not merged.empty else 0
    volatility_pct = calculate_volatility(merged["portfolio_return"])
    sharpe_ratio = calculate_sharpe(merged["portfolio_return"])

    stats = {
        "final_capital": round(final_capital, 2),
        "total_return_pct": round(total_return_pct, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "volatility_pct": round(volatility_pct, 2) if volatility_pct is not None else None,
        "sharpe_ratio": round(sharpe_ratio, 4) if sharpe_ratio is not None else None,
        "trades": len(merged)
    }

    return merged, stats


def add_text_page(pdf, title, lines):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    plt.axis("off")

    y = 0.95
    plt.text(0.05, y, title, fontsize=18, fontweight="bold", va="top")
    y -= 0.05

    for line in lines:
        plt.text(0.05, y, line, fontsize=11, va="top")
        y -= 0.03
        if y < 0.05:
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.patch.set_facecolor("white")
            plt.axis("off")
            y = 0.95

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def add_dataframe_page(pdf, title, df, max_rows=20):
    fig = plt.figure(figsize=(11.69, 8.27))
    plt.axis("off")
    plt.title(title, fontsize=16, fontweight="bold", pad=20)

    show_df = df.head(max_rows).copy()

    table = plt.table(
        cellText=show_df.values,
        colLabels=show_df.columns,
        loc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.4)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def add_image_page(pdf, title, image_path: Path):
    if not image_path.exists():
        return

    img = plt.imread(image_path)

    fig = plt.figure(figsize=(11.69, 8.27))
    plt.suptitle(title, fontsize=16, fontweight="bold")
    plt.imshow(img)
    plt.axis("off")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def generate_strategy_report(summary_df, risk_df, compare_df, last_update):
    top_strategy = compare_df.sort_values("final_capital", ascending=False).iloc[0]

    title_lines = [
        "Project: Precious Metal Premium Mean-Reversion Strategy",
        "",
        f"Last Update Time: {last_update['last_update_time']}",
        f"Update Status: {last_update['status']}",
        f"Update Message: {last_update['message']}",
        "",
        "Best Strategy Summary",
        f"- Asset: {top_strategy['asset']}",
        f"- Signal: {top_strategy['signal']}",
        f"- Holding Days: {top_strategy['holding_days']}",
        f"- Final Capital: {top_strategy['final_capital']}",
        f"- Total Return %: {top_strategy['total_return_pct']}",
        f"- Trades: {top_strategy['trades']}",
        "",
        "Core Findings",
        "- BUY strategies outperform SELL strategies in the last 2 years.",
        "- Silver BUY strategies show the strongest returns.",
        "- Silver BUY 20D is currently the best-performing strategy."
    ]

    with PdfPages(PDF_OUTPUT_PATH) as pdf:
        add_text_page(pdf, "Strategy Report", title_lines)
        add_dataframe_page(pdf, "Backtest Summary Table", summary_df, max_rows=20)
        add_dataframe_page(pdf, "Risk Metrics Table", risk_df, max_rows=20)
        add_dataframe_page(pdf, "Strategy Ranking Table", compare_df, max_rows=20)

        add_image_page(pdf, "Equity Curve Comparison", CHARTS_DIR / "equity_curve_comparison_all_strategies.png")
        add_image_page(pdf, "Backtest Average Return", CHARTS_DIR / "backtest_avg_return.png")
        add_image_page(pdf, "Backtest Win Rate", CHARTS_DIR / "backtest_win_rate.png")
        add_image_page(pdf, "Gold Z-score Signals", CHARTS_DIR / "gold_zscore_2year_signal.png")
        add_image_page(pdf, "Silver Z-score Signals", CHARTS_DIR / "silver_zscore_2year_signal.png")

    return PDF_OUTPUT_PATH


def report_dependencies() -> list[Path]:
    return [
        SUMMARY_PATH,
        RISK_PATH,
        COMPARE_PATH,
        LAST_UPDATE_PATH,
        CHARTS_DIR / "equity_curve_comparison_all_strategies.png",
        CHARTS_DIR / "backtest_avg_return.png",
        CHARTS_DIR / "backtest_win_rate.png",
        CHARTS_DIR / "gold_zscore_2year_signal.png",
        CHARTS_DIR / "silver_zscore_2year_signal.png",
    ]


def is_pdf_stale(pdf_path: Path) -> bool:
    if not pdf_path.exists():
        return True

    pdf_mtime = pdf_path.stat().st_mtime
    for path in report_dependencies():
        if path.exists() and path.stat().st_mtime > pdf_mtime:
            return True

    return False


def ensure_fresh_pdf_report(summary_df, risk_df, compare_df, last_update) -> Path:
    if is_pdf_stale(PDF_OUTPUT_PATH):
        return generate_strategy_report(summary_df, risk_df, compare_df, last_update)
    return PDF_OUTPUT_PATH


# ===== 讀資料 =====
premium_df, backtest_df, risk_df, summary_df, compare_df = load_data()
last_update = load_last_update()
market_panel = get_market_panel_data(premium_df)
today_signal = get_today_signal(premium_df)

# ===== 標題 =====
st.title("Precious Metal Quant Dashboard")
st.caption("Gold / Silver Futures-Spot Premium | Z-score Signals | Backtest | Risk Metrics")

# ===== 側邊欄 =====
st.sidebar.header("Strategy Selector")

asset = st.sidebar.selectbox("Asset", ["gold", "silver"])
signal = st.sidebar.selectbox("Signal", ["BUY", "SELL"])
holding_days = st.sidebar.selectbox("Holding Days", [5, 10, 20])

st.sidebar.markdown("---")
st.sidebar.subheader("Portfolio Simulator")

gold_weight = st.sidebar.slider("Gold Weight", 0, 100, 50, 5)
silver_weight = st.sidebar.slider("Silver Weight", 0, 100, 50, 5)

gold_port_holding = st.sidebar.selectbox("Gold BUY Holding Days", [5, 10, 20], index=2)
silver_port_holding = st.sidebar.selectbox("Silver BUY Holding Days", [5, 10, 20], index=2)

if st.sidebar.button("Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()

# ===== 更新狀態 =====
status_icon = "🟢" if last_update["status"] == "success" else "🔴"

st.markdown(
    f"""
**Last Update**: {last_update["last_update_time"]}  
**Status**: {status_icon} {last_update["status"]}  
**Message**: {last_update["message"]}
"""
)

# ===== PDF Report 按鈕 =====
st.subheader("Strategy Report Export")

r1, r2 = st.columns([1, 2])

with r1:
    if st.button("📄 Generate Strategy Report PDF"):
        try:
            pdf_path = generate_strategy_report(summary_df, risk_df, compare_df, last_update)
            st.success(f"PDF 已生成：{pdf_path.name}")
        except Exception as e:
            st.error(f"生成 PDF 失敗：{e}")

with r2:
    try:
        pdf_path = ensure_fresh_pdf_report(summary_df, risk_df, compare_df, last_update)
    except Exception as e:
        pdf_path = None
        st.error(f"準備 PDF 失敗：{e}")

    if pdf_path and pdf_path.exists():
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Strategy Report PDF",
                data=f,
                file_name="strategy_report.pdf",
                mime="application/pdf"
            )

# ===== 市場價格面板 =====
st.subheader("Market Panel")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Gold Futures", f"{market_panel['gold_futures']:.2f}")
m2.metric("Silver Futures", f"{market_panel['silver_futures']:.2f}")
m3.metric("Gold Spot Proxy", f"{market_panel['gold_spot_proxy']:.2f}")
m4.metric("Silver Spot Proxy", f"{market_panel['silver_spot_proxy']:.2f}")

# ===== 今日訊號 =====
st.subheader("Today Trading Signal")

t1, t2 = st.columns(2)
t1.metric("Gold Signal", today_signal["gold_signal"], f"Z-score {today_signal['gold_z']:.2f}")
t2.metric("Silver Signal", today_signal["silver_signal"], f"Z-score {today_signal['silver_z']:.2f}")

# ===== 篩選後資料 =====
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

latest_date = premium_df["date"].max()
start_date = latest_date - pd.Timedelta(days=730)
recent_2y = premium_df[premium_df["date"] >= start_date].copy()
recent_2y = recent_2y.sort_values("date").reset_index(drop=True)

signal_col = get_signal_col(asset)
zscore_col = get_zscore_col(asset)

buy_points = recent_2y[recent_2y[signal_col] == "BUY"]
sell_points = recent_2y[recent_2y[signal_col] == "SELL"]

# ===== 策略健康度 =====
st.subheader("Strategy Health")

if not selected_risk.empty:
    row = selected_risk.iloc[0]
    h1, h2, h3 = st.columns(3)
    h1.metric("Sharpe Ratio", f"{row['sharpe_ratio']:.4f}")
    h2.metric("Win Rate", f"{row['win_rate_pct']:.2f}%")
    h3.metric("Max Drawdown", f"{row['max_drawdown_pct']:.2f}%")
else:
    st.warning("目前沒有對應策略的風險指標資料。")

# ===== 策略 KPI =====
st.subheader("Strategy KPIs")

if not selected_risk.empty:
    row = selected_risk.iloc[0]
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Final Capital", f"{row['final_capital']:.2f}")
    k2.metric("Total Return %", f"{row['total_return_pct']:.2f}")
    k3.metric("Win Rate %", f"{row['win_rate_pct']:.2f}")
    k4.metric("Max Drawdown %", f"{row['max_drawdown_pct']:.2f}")
    k5.metric("Volatility %", f"{row['volatility_pct']:.2f}")
    k6.metric("Sharpe Ratio", f"{row['sharpe_ratio']:.4f}")
else:
    st.warning("目前沒有對應策略的 KPI 資料。")

# ===== 分頁 =====
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Equity Curve",
    "Z-score Signal",
    "Backtest Table",
    "Strategy Ranking",
    "Portfolio Simulator"
])

with tab1:
    st.subheader(f"Equity Curve | {asset.upper()} {signal} {holding_days}D")
    if not selected_backtest.empty:
        equity_df = build_equity_curve(selected_backtest, initial_capital=10000)
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(equity_df["date"], equity_df["equity"], linewidth=2)
        ax.set_title(f"{asset.upper()} {signal} {holding_days}D")
        ax.set_xlabel("Date")
        ax.set_ylabel("Capital")
        st.pyplot(fig)
    else:
        st.info("這個策略沒有回測資料。")

with tab2:
    st.subheader(f"Z-score Signal View | {asset.upper()}")
    fig2, ax2 = plt.subplots(figsize=(14, 5))
    ax2.plot(recent_2y["date"], recent_2y[zscore_col], linewidth=1.8, label=f"{asset.upper()} Z-score")
    ax2.axhline(2, linestyle="--", linewidth=1.2, label="SELL Threshold (+2)")
    ax2.axhline(-2, linestyle="--", linewidth=1.2, label="BUY Threshold (-2)")
    ax2.axhline(0, linestyle=":", linewidth=1)
    ax2.scatter(buy_points["date"], buy_points[zscore_col], marker="^", s=80, label="BUY")
    ax2.scatter(sell_points["date"], sell_points[zscore_col], marker="v", s=80, label="SELL")
    ax2.set_title(f"{asset.upper()} Z-score with Signals")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Z-score")
    ax2.legend()
    st.pyplot(fig2)

with tab3:
    st.subheader("Backtest Detail")
    if not selected_backtest.empty:
        st.dataframe(selected_backtest, width="stretch")
    else:
        st.info("這個策略沒有回測明細資料。")

with tab4:
    st.subheader("All Strategy Ranking")
    ranking_df = summary_df.sort_values("avg_return_pct", ascending=False).reset_index(drop=True)
    st.dataframe(ranking_df, width="stretch")

with tab5:
    st.subheader("Portfolio Simulator | BUY Strategies Only")

    portfolio_df, portfolio_stats = build_portfolio_curve(
        backtest_df=backtest_df,
        gold_holding_days=gold_port_holding,
        silver_holding_days=silver_port_holding,
        gold_weight=gold_weight,
        silver_weight=silver_weight,
        initial_capital=10000
    )

    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("Final Capital", f"{portfolio_stats['final_capital']:.2f}")
    p2.metric("Total Return %", f"{portfolio_stats['total_return_pct']:.2f}")
    p3.metric("Max Drawdown %", f"{portfolio_stats['max_drawdown_pct']:.2f}")
    p4.metric(
        "Volatility %",
        f"{portfolio_stats['volatility_pct']:.2f}" if portfolio_stats["volatility_pct"] is not None else "N/A"
    )
    p5.metric(
        "Sharpe Ratio",
        f"{portfolio_stats['sharpe_ratio']:.4f}" if portfolio_stats["sharpe_ratio"] is not None else "N/A"
    )

    if not portfolio_df.empty:
        fig3, ax3 = plt.subplots(figsize=(12, 5))
        ax3.plot(portfolio_df["date"], portfolio_df["equity"], linewidth=2)
        ax3.set_title(
            f"Portfolio Equity Curve | Gold {gold_weight}% ({gold_port_holding}D) + "
            f"Silver {silver_weight}% ({silver_port_holding}D)"
        )
        ax3.set_xlabel("Date")
        ax3.set_ylabel("Capital")
        st.pyplot(fig3)

        st.subheader("Portfolio Detail")
        st.dataframe(portfolio_df, width="stretch")
    else:
        st.info("目前沒有可用的投組資料。")
