import yfinance as yf
import os

# Create the raw data folder if it doesn't exist
os.makedirs("data/raw", exist_ok=True)

# Download SPY 1-day OHLCV data for the last 30 days
df = yf.download("SPY", period="30d", interval="1d")

# Save the data to a CSV
csv_path = "data/raw/spy_1d_raw.csv"
df.to_csv(csv_path)

print(f"✅ Data downloaded and saved to {csv_path}")
print(df.head())
