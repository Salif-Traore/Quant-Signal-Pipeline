import yfinance as yf
import os

os.makedirs("data/raw", exist_ok=True)

df = yf.download("SPY", period="1d", interval="1d")

csv_path = "data/raw/spy_1d_raw.csv"
df.to_csv(csv_path)

print(f"✅ Data downloaded and saved to {csv_path}")
print(df.head())
