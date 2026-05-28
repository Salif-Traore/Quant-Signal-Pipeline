from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from configs.config import (
    TICKERS,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
)


LOOKBACK_YEARS = 5


def clean_yfinance_dataframe(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    df.columns = [
        str(col).lower()
        .replace(" ", "_")
        for col in df.columns
    ]

    if "adj_close" not in df.columns and "adj close" in df.columns:
        df = df.rename(columns={"adj close": "adj_close"})

    if "date" not in df.columns:
        if "datetime" in df.columns:
            df = df.rename(columns={"datetime": "date"})
        else:
            raise ValueError(f"No date column found for {ticker}")

    df["date"] = pd.to_datetime(df["date"])

    df["ticker"] = ticker
    df["original_ticker"] = ticker

    keep_cols = [
        "date",
        "ticker",
        "original_ticker",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]

    existing_cols = [
        col for col in keep_cols
        if col in df.columns
    ]

    df = df[existing_cols]

    df = df.sort_values("date")

    df = df.drop_duplicates(subset=["date"])

    return df


def download_ticker(ticker: str):
    end_date = datetime.today() + timedelta(days=1)

    start_date = (
        end_date
        - timedelta(days=LOOKBACK_YEARS * 365)
    )

    print(f"\nDownloading {ticker}...")

    raw_df = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if raw_df.empty:
        print(f"FAILED: No data for {ticker}")
        return

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_output = RAW_DATA_DIR / f"{ticker}.parquet"

    processed_output = (
        PROCESSED_DATA_DIR / f"{ticker}.parquet"
    )

    raw_df.to_parquet(raw_output)

    processed_df = clean_yfinance_dataframe(
        raw_df,
        ticker,
    )

    processed_df.to_parquet(processed_output)

    latest_date = (
        processed_df["date"]
        .max()
        .date()
    )

    print(f"Saved raw: {raw_output}")
    print(f"Saved processed: {processed_output}")
    print(f"Latest date: {latest_date}")


def main():
    for ticker in TICKERS:
        try:
            download_ticker(ticker)

        except Exception as e:
            print(f"FAILED: {ticker}")
            print(e)

    print("\nData download complete.")


if __name__ == "__main__":
    main()