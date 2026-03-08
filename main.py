from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent


def run_script(script_path: str) -> None:
    full_path = PROJECT_ROOT / script_path
    print(f"\nRunning: {full_path}")
    result = subprocess.run([sys.executable, str(full_path)])
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {script_path}")


def main() -> None:
    run_script("extract/futures_yfinance.py")
    run_script("transform/compute_signals.py")
    run_script("load/to_sqlite.py")
    print("\nETL Pipeline Finished Successfully")


if __name__ == "__main__":
    main()

from transform.calculate_premium import calculate_premium
from load.save_to_csv import save_data


def run_pipeline():
    print("開始計算溢價率與 Z-score 訊號...")

    df = calculate_premium()

    print("\n前五筆資料：")
    print(df[[
        "date",
        "gold_premium_pct", "gold_zscore", "gold_signal_z",
        "silver_premium_pct", "silver_zscore", "silver_signal_z"
    ]].head())

    recent_60 = df.tail(60)

    print("\n最近60天黃金與白銀 Z-score 訊號：")
    print(recent_60[[
        "date",
        "gold_premium_pct", "gold_zscore", "gold_signal_z",
        "silver_premium_pct", "silver_zscore", "silver_signal_z"
    ]])

    print("\n最近60天黃金訊號統計：")
    print(recent_60["gold_signal_z"].value_counts())

    print("\n最近60天白銀訊號統計：")
    print(recent_60["silver_signal_z"].value_counts())

    print("\n開始輸出資料...")
    save_data(df)

    print("Pipeline 完成！")


if __name__ == "__main__":
    run_pipeline()