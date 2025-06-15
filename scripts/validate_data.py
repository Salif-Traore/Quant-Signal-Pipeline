import os
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

tickers = [
    'AAPL', 'AGG', 'BTC-USD', 'EURUSD', 'GLD', 'IWM', 'MSFT',
    'QQQ', 'SLV', 'SPY', 'TLT', 'USO', 'XLF', 'XLV', 'VIX'
]

DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'

def load_data(ticker):
    file_path = DATA_DIR / f"{ticker}.parquet"
    if not file_path.exists():
        logging.error(f"File not found: {file_path}")
        return None
    try:
        df = pd.read_parquet(file_path)
        logging.info(f"Loaded {ticker} with {len(df)} rows.")
        return df
    except Exception as e:
        logging.error(f"Error loading {ticker}: {e}")
        return None

def check_nulls(df, ticker):
    null_columns = df.columns[df.isnull().any()]
    if len(null_columns) > 0:
        logging.warning(f"{ticker} has nulls in columns: {list(null_columns)}")
    else:
        logging.info(f"{ticker} has no null values.")

def validate_timestamps(all_timestamps):
    if not all_timestamps:
        logging.error("No timestamps collected, skipping timestamp validation.")
        return
    
    common_dates = set.intersection(*all_timestamps.values())
    logging.info(f"Common timestamps across all tickers: {len(common_dates)}")

    for ticker, timestamps in all_timestamps.items():
        missing_dates = timestamps - common_dates
        extra_dates = common_dates - timestamps

        if missing_dates:
            logging.warning(f"{ticker} has {len(missing_dates)} dates missing compared to common timestamps.")
        if extra_dates:
            logging.warning(f"{ticker} has {len(extra_dates)} extra dates not in common timestamps.")


def main():
    all_timestamps = {}
    for ticker in tickers:
        df = load_data(ticker)
        if df is None:
            continue

        check_nulls(df, ticker)

        # Get timestamps index or Date column
        if df.index.name == 'Date':
            timestamps = set(df.index)
        elif 'Date' in df.columns:
            timestamps = set(df['Date'])
        else:
            logging.error(f"{ticker} data missing 'Date' index or column.")
            continue

        all_timestamps[ticker] = timestamps

    if len(all_timestamps) == len(tickers):
        validate_timestamps(all_timestamps)
    else:
        logging.warning("Not all tickers loaded successfully. Skipping timestamp consistency check.")

if __name__ == "__main__":
    main()
