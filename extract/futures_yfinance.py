from __future__ import annotations

from pathlib import Path
import pandas as pd
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "extract" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_futures(symbol: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """
    Download futures OHLCV data from Yahoo Finance via yfinance.
    symbol example: "GC=F" (Gold), "SI=F" (Silver)
    """
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)

    if df is None or df.empty:
        raise RuntimeError(f"No data returned for symbol={symbol}")

    # Ensure index name and timezone-naive timestamps
    df.index.name = "Date"
    # yfinance sometimes returns multi-index columns; flatten if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join([str(x) for x in col if x]) for col in df.columns]

    # Standardize column names
    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )

    return df


def save_to_csv(df: pd.DataFrame, filename: str) -> Path:
    out_path = DATA_DIR / filename
    df.to_csv(out_path)
    return out_path


def main() -> None:
    mapping = {
        "gold_futures": "GC=F",
        "silver_futures": "SI=F",
    }

    for name, symbol in mapping.items():
        print(f"Downloading {name} ({symbol})...")
        df = download_futures(symbol, period="5y", interval="1d")
        out = save_to_csv(df, f"{name}.csv")
        print(f"Saved: {out} | rows={len(df)} | last_date={df.index.max()}")

    print("Done.")


if __name__ == "__main__":
    main()