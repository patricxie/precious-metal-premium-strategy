import subprocess
import sys
from pathlib import Path


def main():
    base_dir = Path(__file__).resolve().parent
    dashboard_path = base_dir / "dashboard_app.py"

    if not dashboard_path.exists():
        raise FileNotFoundError(f"找不到 dashboard_app.py：{dashboard_path}")

    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(dashboard_path)],
        check=True
    )


if __name__ == "__main__":
    main()