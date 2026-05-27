import os
import pandas as pd
import yfinance as yf

from features.twelve_month_return_feature import TwelveMonthReturnFeature
from features.twelve_month_return_signal_feature import TwelveMonthReturnSignalFeature

# === Config ===
PREPARED_DIR = "data/prepared"
TICKERS = [
    "AAPL", "MSFT", "SPY", "QQQ", "IWM",
    "GLD", "SLV", "USO", "TLT", "EURUSD=X",
    "BTC-USD", "XLF", "XLV", "AGG", "^VIX"
]

def prepare_data(ticker):
    print(f"\n📈 Downloading data for {ticker}...")
    df = yf.download(ticker, period="3y", interval="1d")

    if df.empty:
        print(f"❌ No data downloaded for {ticker}.")
        return

    # Flatten MultiIndex columns if any
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Close" not in df.columns:
        print(f"❌ 'Close' column not found in {ticker} data.")
        return

    df = df[["Close"]].copy()

    # Compute excess 12-month return feature
    return_feature = TwelveMonthReturnFeature()
    df[return_feature.name] = return_feature.apply(df)

    # Step 2: Print excess_12m_return values for debugging
    print(f"Excess 12m return sample for {ticker}:")
    print(df[[return_feature.name]].tail(10))

    # Compute 12-month return signal feature (+1, -1, 0)
    signal_feature = TwelveMonthReturnSignalFeature()
    df[signal_feature.name] = signal_feature.apply(df)

    # Step 4: Print signal column after applying signal for debugging
    print(f"Signal 12m return sample for {ticker}:")
    print(df[[return_feature.name, signal_feature.name]].tail(10))

    # Drop rows with NaNs in either column
    df = df.dropna(subset=[return_feature.name, signal_feature.name])

    # Step 5: Final print before saving
    print(f"Final features sample for {ticker}:")
    print(df[[return_feature.name, signal_feature.name]].tail(10))

    os.makedirs(PREPARED_DIR, exist_ok=True)
    save_path = os.path.join(PREPARED_DIR, f"{ticker}_with_features.parquet")
    df.to_parquet(save_path)
    print(f"✅ Saved prepared data to {save_path}")

if __name__ == "__main__":
    for ticker in TICKERS:
        prepare_data(ticker)
