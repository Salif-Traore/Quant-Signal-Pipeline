import os
import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from features.base_features import PercentChangeFeature

def process_ticker_file(parquet_path: Path, price_col_prefix='Close'):
    print(f"Processing {parquet_path.name} ...")
    df = pd.read_parquet(parquet_path)
    print(f"Loaded raw data with {len(df)} rows")

    # Flatten multi-index columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df.columns]
        print(f"Flattened columns: {list(df.columns)}")

    # Determine full price column name for percent change (e.g. Close_AAPL)
    ticker = parquet_path.stem  # filename without extension
    price_col = f"{price_col_prefix}_{ticker}"

    if price_col not in df.columns:
        print(f"Warning: Price column '{price_col}' not found in {parquet_path.name}. Skipping...")
        return

    # Calculate percent change feature
    feature = PercentChangeFeature(price_col=price_col)
    df['pct_change'] = feature.calculate(df)

    # Save processed file
    output_path = parquet_path.parent.parent / 'prepared' / f"{ticker}_with_features.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path)
    print(f"Saved data with features to {output_path}\n")

def main():
    raw_data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    parquet_files = list(raw_data_dir.glob("*.parquet"))

    print(f"Found {len(parquet_files)} parquet files to process.")

    for parquet_file in parquet_files:
        process_ticker_file(parquet_file)

if __name__ == "__main__":
    main()
