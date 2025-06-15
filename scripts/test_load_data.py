from loaders.parquet_loader import load_parquet

file_path = 'data/raw/spy_1d_raw.parquet'

df = load_parquet(file_path)

print(df.head())
