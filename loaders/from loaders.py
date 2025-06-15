from loaders.parquet_loader import load_parquet
import os

# Update with your actual path to a parquet file (you can make a dummy one or download one from yfinance)
file_path = "data/SPY.parquet"

if os.path.exists(file_path):
    df = load_parquet(file_path)
    print(df.head())
else:
    print("Parquet file not found:", file_path)
