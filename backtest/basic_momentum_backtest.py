import os
import pandas as pd
from loaders.parquet_loader import load_parquet

# === Config ===
DATA_DIR = "data/raw"
TICKER = "SPY"
MA_WINDOW = 20  # Moving average window
INITIAL_CAPITAL = 10000

def run_backtest(file_path):
    df = load_parquet(file_path)

    if 'Adj Close' not in df.columns:
        raise ValueError("Expected 'Adj Close' column in data.")

    df = df.copy()
    df['MA'] = df['Adj Close'].rolling(MA_WINDOW).mean()
    df['Signal'] = 0
    df.loc[df['Adj Close'] > df['MA'], 'Signal'] = 1  # Buy when price > MA
    df['Position'] = df['Signal'].shift(1)  # Lag signal to avoid lookahead bias
    df['Daily Return'] = df['Adj Close'].pct_change()
    df['Strategy Return'] = df['Daily Return'] * df['Position']

    df['Equity Curve'] = (1 + df['Strategy Return']).cumprod() * INITIAL_CAPITAL

    return df

if __name__ == "__main__":
    file_path = os.path.join(DATA_DIR, f"{TICKER}.parquet")
    if not os.path.exists(file_path):
        print(f"Missing file: {file_path}")
    else:
        result = run_backtest(file_path)
        print(result[['Adj Close', 'MA', 'Signal', 'Position', 'Strategy Return', 'Equity Curve']].tail())

        # Optional: save result
        result.to_csv(f"results/{TICKER}_momentum_backtest.csv")
