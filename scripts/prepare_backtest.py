import os
import pandas as pd

RAW_DIR = "data/raw"
PREPARED_DIR = "data/prepared"
os.makedirs(PREPARED_DIR, exist_ok=True)

TICKERS = [
    "AAPL", "MSFT", "SPY", "QQQ", "IWM", "GLD", "SLV", "USO",
    "TLT", "EURUSD", "BTC-USD", "XLF", "XLV", "AGG", "VIX"
]

def prepare_data(ticker):
    file_path = f"{RAW_DIR}/{ticker}.parquet"
    df = pd.read_parquet(file_path)
    
    # Add percent price change column
    df['pct_change'] = df['Close'].pct_change()
    
    # Optional: Drop the first row (NaN pct_change)
    df = df.dropna(subset=['pct_change'])
    
    # Save prepared data
    df.to_parquet(f"{PREPARED_DIR}/{ticker}.parquet")
    print(f"Prepared {ticker}")

if __name__ == "__main__":
    for ticker in TICKERS:
        prepare_data(ticker)
