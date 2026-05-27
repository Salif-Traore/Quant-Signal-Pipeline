from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from configs.config import (
    PREPARED_DATA_DIR,
    PROCESSED_DATA_DIR,
)
from features.momentum_features import build_features


PREPARED_DATA_DIR.mkdir(exist_ok=True)


all_feature_frames = []

parquet_files = list(PROCESSED_DATA_DIR.glob("*.parquet"))

for file_path in parquet_files:

    ticker = file_path.stem

    print(f"Processing {ticker}...")

    df = pd.read_parquet(file_path)

    try:

        featured = build_features(df, ticker=ticker)

        output_path = (
            PREPARED_DATA_DIR
            / f"{ticker}_with_features.parquet"
        )

        featured.to_parquet(output_path)

        all_feature_frames.append(featured)

        print(f"Saved {output_path.name}")

    except Exception as e:

        print(f"FAILED: {ticker}")
        print(e)


if all_feature_frames:

    combined = pd.concat(
        all_feature_frames,
        ignore_index=True
    )

    combined_output = (
        PREPARED_DATA_DIR
        / "all_features.parquet"
    )

    combined.to_parquet(combined_output)

    print(
        f"Saved combined feature dataset: "
        f"{combined_output.name}"
    )

print("Feature pipeline complete.")