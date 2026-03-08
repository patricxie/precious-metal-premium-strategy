import requests
import pandas as pd
from pathlib import Path

API_KEY = "5P21PXQOM47O0P2T"


def fetch_one_metal(symbol: str, output_filename: str, output_col: str):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GOLD_SILVER_HISTORY",
        "symbol": symbol,
        "interval": "daily",
        "apikey": API_KEY
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    print(f"{symbol} response keys: {list(data.keys())}")

    if "data" not in data:
        raise ValueError(f"{symbol} API 回傳格式不正確: {data}")

    df = pd.DataFrame(data["data"])
    print(f"{symbol} 原始欄位: {df.columns.tolist()}")

    df = df[["date", "price"]].copy()
    df.columns = ["date", output_col]

    df["date"] = pd.to_datetime(df["date"])
    df[output_col] = pd.to_numeric(df[output_col], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)

    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "extract" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / output_filename
    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path} | rows={len(df)} | last_date={df['date'].max()}")


def main():
    print("Downloading gold_spot from Alpha Vantage...")
    fetch_one_metal("GOLD", "gold_spot.csv", "gold_spot")

    print("Downloading silver_spot from Alpha Vantage...")
    fetch_one_metal("SILVER", "silver_spot.csv", "silver_spot")

    print("Done.")


if __name__ == "__main__":
    main()