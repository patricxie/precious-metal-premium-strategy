import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

LAST_UPDATE_PATH = PROCESSED_DIR / "last_update.json"
LOG_PATH = PROCESSED_DIR / "daily_update_log.txt"


def run_script(script_name: str):
    script_path = BASE_DIR / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"找不到檔案：{script_path}")

    print(f"\nRunning: {script_path}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    log_text = (
        f"\n{'=' * 80}\n"
        f"[{datetime.now().isoformat()}] {script_name}\n"
        f"Return code: {result.returncode}\n\n"
        f"STDOUT:\n{result.stdout}\n\n"
        f"STDERR:\n{result.stderr}\n"
    )

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_text)

    print("----- STDOUT -----")
    print(result.stdout if result.stdout else "(empty)")
    print("----- STDERR -----")
    print(result.stderr if result.stderr else "(empty)")

    if result.returncode != 0:
        raise RuntimeError(f"{script_name} 執行失敗，請查看 {LOG_PATH}")

    print(f"{script_name} 執行成功")


def write_last_update(status: str, message: str):
    payload = {
        "last_update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "message": message,
    }
    with open(LAST_UPDATE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    try:
        scripts = [
            "main.py",
            "analysis_backtest.py",
            "analysis_risk_metrics.py",
            "analysis_summary_table.py",
            "analysis_equity_curve_compare.py",
            "analysis_plot_backtest.py",
            "analysis_plot_zscore_signals.py",
        ]

        for script in scripts:
            run_script(script)

        write_last_update("success", "每日資料更新完成")
        print("\nDaily update completed successfully.")

    except Exception as e:
        write_last_update("failed", str(e))
        print(f"\nDaily update failed: {e}")
        raise


if __name__ == "__main__":
    main()