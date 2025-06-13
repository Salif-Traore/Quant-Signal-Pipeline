import pandas as pd

def load_parquet(file_path):
    """Load parquet file into DataFrame."""
    return pd.read_parquet(file_path)
