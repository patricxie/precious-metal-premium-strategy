from __future__ import annotations

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent


def run_script(script_path: str) -> None:
    full_path = PROJECT_ROOT / script_path
    print(f"\nRunning: {full_path}")
    result = subprocess.run([sys.executable, str(full_path)], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {script_path}")


def main() -> None:
    scripts = [
        "extract/futures_yfinance.py",
        "transform/compute_signals.py",
        "load/to_sqlite.py",
    ]

    for script in scripts:
        run_script(script)

    print("\nETL pipeline finished successfully.")


if __name__ == "__main__":
    main()
