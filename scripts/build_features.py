from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PREPARED_DIR = PROJECT_ROOT / "data" / "prepared"

def clean_name(name):
    return name.replace("=", "").replace("^", "")

def main():
    PREPARED_DIR.mkdir(parents=True, exist_ok=True)
    frames = []

    for path in sorted(RAW_DIR.glob("*.parquet")):
        df = pd.read_parquet(path)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]

        df = df.reset_index()

        date_col = "Date" if "Date" in df.columns else df.columns[0]
        close_col = "Close" if "Close" in df.columns else None

        if close_col is None:
            print(f"Skipping {path.name}: no Close column")
            continue

        ticker = clean_name(path.stem)

        out = df[[date_col, close_col]].copy()
        out.columns = ["Date", "Close"]

        out["Date"] = pd.to_datetime(out["Date"], errors="coerce").dt.tz_localize(None)
        out["Close"] = pd.to_numeric(out["Close"], errors="coerce")
        out = out.dropna(subset=["Date", "Close"]).sort_values("Date")

        out["ticker"] = ticker
        out["daily_return"] = out["Close"].pct_change(fill_method=None)
        out["ts_momentum_12m"] = out["Close"].pct_change(252, fill_method=None)

        out.to_parquet(PREPARED_DIR / f"{ticker}_with_features.parquet", index=False)
        frames.append(out)

        print(f"Saved {ticker}_with_features.parquet")

    panel = pd.concat(frames, ignore_index=True)
    panel = panel.drop_duplicates(["Date", "ticker"])
    panel["xs_momentum_rank"] = panel.groupby("Date")["ts_momentum_12m"].rank(ascending=False)

    panel.to_parquet(PREPARED_DIR / "all_features.parquet", index=False)
    print("Saved all_features.parquet")

if __name__ == "__main__":
    main()
