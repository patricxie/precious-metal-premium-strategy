from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHARTS_DIR = PROCESSED_DIR / "charts"

SUMMARY_PATH = PROCESSED_DIR / "recent_2year_backtest_report_table.csv"
RISK_PATH = PROCESSED_DIR / "recent_2year_risk_metrics.csv"
COMPARE_PATH = PROCESSED_DIR / "equity_curve_comparison_all_strategies.csv"
LAST_UPDATE_PATH = PROCESSED_DIR / "last_update.json"

PDF_OUTPUT_PATH = PROCESSED_DIR / "strategy_report.pdf"


def load_json(path: Path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "last_update_time": "N/A",
        "status": "unknown",
        "message": "No update info"
    }


def add_text_page(pdf, title, lines):
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
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
    fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
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


def main():
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(f"找不到檔案：{SUMMARY_PATH}")
    if not RISK_PATH.exists():
        raise FileNotFoundError(f"找不到檔案：{RISK_PATH}")
    if not COMPARE_PATH.exists():
        raise FileNotFoundError(f"找不到檔案：{COMPARE_PATH}")

    summary_df = pd.read_csv(SUMMARY_PATH)
    risk_df = pd.read_csv(RISK_PATH)
    compare_df = pd.read_csv(COMPARE_PATH)
    last_update = load_json(LAST_UPDATE_PATH)

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
        "- Silver BUY 20D is currently the best-performing strategy.",
    ]

    with PdfPages(PDF_OUTPUT_PATH) as pdf:
        add_text_page(pdf, "Strategy Report", title_lines)
        add_dataframe_page(pdf, "Backtest Summary Table", summary_df, max_rows=20)
        add_dataframe_page(pdf, "Risk Metrics Table", risk_df, max_rows=20)
        add_dataframe_page(pdf, "Strategy Ranking Table", compare_df, max_rows=20)

        add_image_page(
            pdf,
            "Equity Curve Comparison",
            CHARTS_DIR / "equity_curve_comparison_all_strategies.png"
        )
        add_image_page(
            pdf,
            "Backtest Average Return",
            CHARTS_DIR / "backtest_avg_return.png"
        )
        add_image_page(
            pdf,
            "Backtest Win Rate",
            CHARTS_DIR / "backtest_win_rate.png"
        )
        add_image_page(
            pdf,
            "Gold Z-score Signals",
            CHARTS_DIR / "gold_zscore_2year_signal.png"
        )
        add_image_page(
            pdf,
            "Silver Z-score Signals",
            CHARTS_DIR / "silver_zscore_2year_signal.png"
        )

    print(f"Strategy report PDF 已儲存到：{PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
