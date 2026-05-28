from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from configs.config import PREPARED_DATA_DIR, TRADABLE_TICKERS
from signals.momentum_signals import build_cross_sectional_momentum_signal
from portfolio.construction import build_monthly_rebalanced_portfolio


def main():
    features_path = PREPARED_DATA_DIR / "all_features.parquet"

    df = pd.read_parquet(features_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])

    signal_df = build_cross_sectional_momentum_signal(df)

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = build_monthly_rebalanced_portfolio(signal_df)

    latest_date = portfolio_df["date"].max()

    live_signals = portfolio_df[
        (portfolio_df["date"] == latest_date)
        & (portfolio_df["weight"] > 0)
    ].copy()

    cols = [
        "date",
        "ticker",
        "weight",
        "mom_1m",
        "vol_1m",
        "returns",
        "signal_rank",
        "vol_rank",
    ]

    existing_cols = [col for col in cols if col in live_signals.columns]

    live_signals = live_signals[existing_cols]
    live_signals = live_signals.sort_values("weight", ascending=False)

    output_dir = PREPARED_DATA_DIR.parent / "live"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "latest_signals.csv"

    live_signals.to_csv(output_path, index=False)

    print("\nLive Signals")
    print("-" * 40)
    print(f"Signal date: {latest_date.date()}")
    print(live_signals.to_string(index=False))

    print("\nSaved:")
    print(output_path)


if __name__ == "__main__":
    main()