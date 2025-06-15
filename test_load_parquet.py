import pandas as pd

def test_load_parquet():
    parquet_path = 'data/raw/spy_1d_raw.parquet'
    df = pd.read_parquet(parquet_path)
    print(df.head())

if __name__ == '__main__':
    test_load_parquet()
