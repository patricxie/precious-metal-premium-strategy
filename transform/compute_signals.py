from __future__ import annotations

from pathlib import Path
import pandas as pd


# ---------- Paths ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTRACT_DIR = PROJECT_ROOT / "extract" / "data"
TRANSFORM_DIR = PROJECT_ROOT / "transform" / "data"
TRANSFORM_DIR.mkdir(parents=True, exist_ok=True)


# ---------- IO ----------
def load_futures_csv(path: Path) -> pd.DataFrame:
    """
    Robust CSV loader.
    Supports:
      1) CSV with header including Date/Open/High/Low/Close/Adj Close/Volume
      2) CSV without header (7 columns)
      3) Mixed column name cases / spaces
    Returns:
      DataFrame indexed by Date with normalized lowercase columns:
        open, high, low, close, adj_close, volume
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    # First try: read with header
    df = pd.read_csv(path)

    # Case A: has a Date column
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date").set_index("Date")

        # normalize column names
        cols = []
        for c in df.columns:
            c2 = str(c).strip().lower().replace(" ", "_")
            cols.append(c2)
        df.columns = cols

    else:
        # Case B: no header (or header corrupted) -> force schema
        df = pd.read_csv(
            path,
            header=None,
            names=["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"],
        )
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).sort_values("Date").set_index("Date")
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # If yfinance produced multiindex-flattened columns like close_gc=f, find/rename to close
    # Prefer exact matches first
    rename_map = {}
    if "adj_close" not in df.columns:
        # Sometimes it's adjclose
        for c in df.columns:
            if c.replace("_", "") == "adjclose":
                rename_map[c] = "adj_close"
                break

    # If 'close' doesn't exist, try to map any column containing 'close' to close
    if "close" not in df.columns:
        for c in df.columns:
            if "close" in c and "adj" not in c:
                rename_map[c] = "close"
                break

    # Same for open/high/low/volume if missing
    for base in ["open", "high", "low", "volume"]:
        if base not in df.columns:
            for c in df.columns:
                if base in c:
                    rename_map[c] = base
                    break

    if rename_map:
        df = df.rename(columns=rename_map)

    required = {"close"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns {missing}. Available columns: {list(df.columns)}")

    return df


# ---------- Features ----------
def add_features(df: pd.DataFrame, price_col: str = "close") -> pd.DataFrame:
    out = df.copy()

    # daily return
    out["ret_1d"] = out[price_col].pct_change()

    # moving averages
    out["ma_20"] = out[price_col].rolling(20).mean()
    out["ma_60"] = out[price_col].rolling(60).mean()

    # deviation from MA20 (percent)
    out["dev_ma20"] = (out[price_col] - out["ma_20"]) / out["ma_20"]

    # z-score of deviation (rolling)
    roll = out["dev_ma20"].rolling(60)
    out["dev_ma20_z"] = (out["dev_ma20"] - roll.mean()) / roll.std()

    # trend flags
    out["trend_up"] = out["ma_20"] > out["ma_60"]
    out["trend_down"] = out["ma_20"] < out["ma_60"]

    # simple signals
    out["signal"] = "HOLD"
    out.loc[(out["dev_ma20_z"] <= -1.5) & out["trend_up"], "signal"] = "BUY"
    out.loc[(out["dev_ma20_z"] >= 1.5) & out["trend_down"], "signal"] = "SELL"

    return out


# ---------- Pipeline ----------
def run_one(asset_name: str) -> Path:
    src = EXTRACT_DIR / f"{asset_name}.csv"
    df = load_futures_csv(src)
    feat = add_features(df, price_col="close")

    out_path = TRANSFORM_DIR / f"{asset_name}_features.csv"
    feat.to_csv(out_path)
    return out_path


def main() -> None:
    for asset in ["gold_futures", "silver_futures"]:
        out = run_one(asset)
        # show last rows summary
        tail = pd.read_csv(out).tail(3)
        print(f"Saved: {out}")
        print(tail[["Date", "close", "ma_20", "ma_60", "dev_ma20_z", "signal"]].to_string(index=False))
        print("-" * 70)


if __name__ == "__main__":
    main()