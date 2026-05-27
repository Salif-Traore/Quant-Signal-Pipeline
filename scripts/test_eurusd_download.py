import yfinance as yf
import pandas as pd
import os

PREPARED_DIR = "data/prepared"

ticker = "EURUSD=X"
print(f"Downloading {ticker}...")
df = yf.download(ticker, period="3y", interval="1d")

if df.empty:
    print(f"No data downloaded for {ticker}")
else:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Close"]].copy()
    df["pct_change"] = df["Close"].pct_change()
    df = df.dropna(subset=["pct_change"])

    os.makedirs(PREPARED_DIR, exist_ok=True)
    save_path = os.path.join(PREPARED_DIR, f"{ticker}_with_features.parquet")
    df.to_parquet(save_path)
    print(f"Saved prepared data for {ticker} at {save_path}")
