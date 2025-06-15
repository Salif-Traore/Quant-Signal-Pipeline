import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# List of tickers - keep original form for yfinance download
TICKERS = [
    "AAPL", "MSFT", "SPY", "QQQ", "IWM", "GLD", "SLV", "USO",
    "TLT", "EURUSD=X", "BTC-USD", "XLF", "XLV", "AGG", "^VIX"
]

# Date range: past 3 years
END_DATE = datetime.today()
START_DATE = END_DATE - timedelta(days=3*365)

# Output directory for parquet files
DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

def clean_ticker(ticker):
    # Remove or replace characters that are invalid in filenames
    return ticker.replace("=", "").replace("^", "").replace("/", "-").replace(":", "-")

def download_and_save(ticker):
    try:
        df = yf.download(ticker, start=START_DATE, end=END_DATE, interval='1d')
        if df.empty:
            print(f"⚠️ No data for {ticker}")
            return
        df["Original_Ticker"] = ticker
        safe_ticker = clean_ticker(ticker)
        save_path = os.path.join(DATA_DIR, f"{safe_ticker}.parquet")
        df.to_parquet(save_path)
        print(f"✅ Saved {ticker} as {save_path}")
    except Exception as e:
        print(f"❌ Failed to download {ticker}: {e}")

if __name__ == "__main__":
    for ticker in TICKERS:
        download_and_save(ticker)

