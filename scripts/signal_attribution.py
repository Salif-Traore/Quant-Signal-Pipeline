from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from configs.config import PREPARED_DATA_DIR, TRADABLE_TICKERS
from signals.momentum_signals import build_cross_sectional_momentum_signal
from portfolio.construction import build_monthly_rebalanced_portfolio


FEATURES_PATH = PREPARED_DATA_DIR / "all_features.parquet"
ATTRIBUTION_PATH = PROJECT_ROOT / "data" / "research" / "signal_attribution.csv"


def main():
    features_df = pd.read_parquet(FEATURES_PATH)
    features_df["date"] = pd.to_datetime(features_df["date"])

    signal_df = build_cross_sectional_momentum_signal(features_df)

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = build_monthly_rebalanced_portfolio(signal_df)

    portfolio_df = portfolio_df.sort_values(["ticker", "date"])

    portfolio_df["next_return"] = (
        portfolio_df.groupby("ticker")["returns"]
        .shift(-1)
    )

    portfolio_df["contribution"] = (
        portfolio_df["weight"]
        * portfolio_df["next_return"]
    )

    attribution = (
        portfolio_df.groupby("ticker")
        .agg(
            total_contribution=("contribution", "sum"),
            avg_weight=("weight", "mean"),
            max_weight=("weight", "max"),
            days_held=("weight", lambda x: (x > 0).sum()),
            avg_next_return=("next_return", "mean"),
            avg_mom_1m=("mom_1m", "mean"),
            avg_vol_1m=("vol_1m", "mean"),
        )
        .reset_index()
    )

    attribution["contribution_pct_of_total"] = (
        attribution["total_contribution"]
        / attribution["total_contribution"].sum()
    )

    attribution = attribution.sort_values(
        "total_contribution",
        ascending=False,
    )

    ATTRIBUTION_PATH.parent.mkdir(parents=True, exist_ok=True)

    attribution.to_csv(ATTRIBUTION_PATH, index=False)

    print("\nSignal Attribution")
    print("-" * 50)
    print(attribution.to_string(index=False))

    print("\nSaved:")
    print(ATTRIBUTION_PATH)


if __name__ == "__main__":
    main()