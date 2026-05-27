import pandas as pd
import matplotlib.pyplot as plt
import os

# === Tickers to Validate ===
TICKERS = [
    "AAPL", "MSFT", "SPY", "QQQ", "IWM",
    "GLD", "SLV", "USO", "TLT", "EURUSD=X",
    "BTC-USD", "XLF", "XLV", "AGG", "^VIX"
]

PREPARED_DIR = "data/prepared"

for ticker in TICKERS:
    path = os.path.join(PREPARED_DIR, f"{ticker}_with_features.parquet")

    if not os.path.exists(path):
        print(f"❌ File not found for {ticker}")
        continue

    df = pd.read_parquet(path)

    if "excess_12m_return" not in df.columns:
        print(f"⚠️ Missing 'excess_12m_return' in {ticker}")
        continue

    print(f"\n✅ Plotting: {ticker}")
    df["excess_12m_return"].dropna().plot(
        title=f"{ticker} - Excess 12M Return",
        figsize=(10, 4)
    )
    plt.xlabel("Date")
    plt.ylabel("Excess 12M Return")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
