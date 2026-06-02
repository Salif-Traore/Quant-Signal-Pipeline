from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from configs.config import (
    INITIAL_CAPITAL,
    PREPARED_DATA_DIR,
    TRADABLE_TICKERS,
)

from signals.momentum_signals import build_cross_sectional_momentum_signal
from portfolio.construction import build_monthly_rebalanced_portfolio
from backtesting.engine import run_vectorized_backtest
from reports.metrics import calculate_performance_metrics


def compute_momentum_breadth(df, momentum_col="mom_1m"):
    breadth = df.copy()

    breadth["positive_momentum"] = (
        breadth[momentum_col] > 0
    ).astype(int)

    breadth = (
        breadth.groupby("date")["positive_momentum"]
        .mean()
        .reset_index()
        .rename(columns={"positive_momentum": "momentum_breadth"})
    )

    return breadth


def apply_exposure_scaling(
    portfolio_df,
    features_df,
    min_exposure,
    max_exposure=1.0,
):
    breadth = compute_momentum_breadth(features_df)

    df = portfolio_df.merge(
        breadth,
        on="date",
        how="left",
    )

    df["momentum_breadth"] = df["momentum_breadth"].fillna(0.5)

    df["exposure_multiplier"] = (
        min_exposure
        + (max_exposure - min_exposure) * df["momentum_breadth"]
    )

    df["weight"] = df["weight"] * df["exposure_multiplier"]

    return df


def run_test(df, min_exposure):
    signal_df = build_cross_sectional_momentum_signal(df)

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = build_monthly_rebalanced_portfolio(signal_df)

    scaled_portfolio_df = apply_exposure_scaling(
        portfolio_df=portfolio_df,
        features_df=signal_df,
        min_exposure=min_exposure,
    )

    backtest_df = run_vectorized_backtest(
        scaled_portfolio_df,
        initial_capital=INITIAL_CAPITAL,
    )

    metrics = calculate_performance_metrics(backtest_df)

    metrics["min_exposure"] = min_exposure
    metrics["max_exposure"] = 1.0
    metrics["scaling_variable"] = "mom_1m_breadth"

    return metrics


def main():
    df = pd.read_parquet(PREPARED_DATA_DIR / "all_features.parquet")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])

    min_exposures = [
        0.60,
        0.70,
        0.70,
        0.80,
        0.90,
    ]

    results = []

    for min_exposure in min_exposures:
        print(f"Testing min exposure: {min_exposure:.0%}")

        metrics = run_test(
            df=df,
            min_exposure=min_exposure,
        )

        results.append(metrics)

    results_df = pd.DataFrame(results)

    output_dir = PREPARED_DATA_DIR.parent / "research"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "regime_exposure_sweep.csv"

    results_df.to_csv(output_path, index=False)

    print("\nRegime Exposure Scaling Sweep")
    print("-" * 60)

    print(
        results_df[
            [
                "min_exposure",
                "total_return",
                "annualized_return",
                "volatility",
                "sharpe_ratio",
                "max_drawdown",
            ]
        ].to_string(index=False)
    )

    print("\nSaved:")
    print(output_path)


if __name__ == "__main__":
    main()