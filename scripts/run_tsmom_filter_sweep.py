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

from portfolio.construction import build_monthly_rebalanced_portfolio
from backtesting.engine import run_vectorized_backtest
from reports.metrics import calculate_performance_metrics


def build_hybrid_signal(
    df,
    cross_sectional_momentum_col="mom_1m",
    time_series_filter_col="mom_1m",
    tsmom_threshold=0.0,
    vol_col="vol_1m",
    vol_quantile=0.75,
    top_n=3,
):
    signal_df = df.copy()
    signal_df = signal_df.sort_values(["date", "ticker"])

    signal_df["tsmom_filter"] = (
        signal_df[time_series_filter_col]
        > tsmom_threshold
    ).astype(int)

    signal_df["vol_rank"] = (
        signal_df.groupby("date")[vol_col]
        .rank(pct=True)
    )

    signal_df["eligible"] = (
        (signal_df["tsmom_filter"] == 1)
        & (signal_df["vol_rank"] <= vol_quantile)
    ).astype(int)

    signal_df["raw_rank"] = pd.NA

    eligible_mask = signal_df["eligible"] == 1

    signal_df.loc[eligible_mask, "raw_rank"] = (
        signal_df.loc[eligible_mask]
        .groupby("date")[cross_sectional_momentum_col]
        .rank(ascending=False, method="first")
    )

    signal_df["raw_long_signal"] = (
        signal_df["raw_rank"] <= top_n
    ).astype(int)

    signal_df["long_signal"] = (
        signal_df.sort_values(["ticker", "date"])
        .groupby("ticker")["raw_long_signal"]
        .shift(1)
        .fillna(0)
        .astype(int)
    )

    signal_df["signal_rank"] = signal_df["raw_rank"]

    return signal_df


def run_test(
    df,
    threshold,
):
    signal_df = build_hybrid_signal(
        df,
        tsmom_threshold=threshold,
    )

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = build_monthly_rebalanced_portfolio(signal_df)

    backtest_df = run_vectorized_backtest(
        portfolio_df,
        initial_capital=INITIAL_CAPITAL,
    )

    metrics = calculate_performance_metrics(backtest_df)

    metrics["tsmom_filter_col"] = "mom_1m"
    metrics["tsmom_threshold"] = threshold
    metrics["top_n"] = 3
    metrics["vol_quantile"] = 0.75
    metrics["signal_lagged"] = True

    return metrics


def main():
    df = pd.read_parquet(
        PREPARED_DATA_DIR / "all_features.parquet"
    )

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])

    thresholds = [
        0.00,
        0.01,
        0.03,
        0.05,
    ]

    results = []

    for threshold in thresholds:
        print(f"Testing TSMOM threshold > {threshold:.2%}")

        metrics = run_test(
            df,
            threshold=threshold,
        )

        results.append(metrics)

    results_df = pd.DataFrame(results)

    output_dir = PREPARED_DATA_DIR.parent / "research"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        output_dir
        / "tsmom_threshold_sweep.csv"
    )

    results_df.to_csv(
        output_path,
        index=False,
    )

    print("\nTSMOM Threshold Sweep Results")
    print("-" * 60)

    print(
        results_df[
            [
                "tsmom_threshold",
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