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


TRAIN_YEARS = 3
TEST_MONTHS = 3


def build_candidate_signal(
    df,
    momentum_col="mom_1m",
    vol_col="vol_1m",
    vol_quantile=0.75,
    top_n=3,
):
    signal_df = df.copy()
    signal_df = signal_df.sort_values(["date", "ticker"])

    signal_df["vol_rank"] = (
        signal_df.groupby("date")[vol_col]
        .rank(pct=True)
    )

    signal_df = signal_df[
        signal_df["vol_rank"] <= vol_quantile
    ].copy()

    signal_df["signal_rank"] = (
        signal_df.groupby("date")[momentum_col]
        .rank(ascending=False, method="first")
    )

    signal_df["long_signal"] = (
        signal_df["signal_rank"] <= top_n
    ).astype(int)

    return signal_df


def run_fold(df, train_start, train_end, test_start, test_end, fold_number):
    test_df = df[
        (df["date"] >= test_start)
        & (df["date"] <= test_end)
    ].copy()

    if test_df.empty:
        return None

    signal_df = build_candidate_signal(test_df)

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = build_monthly_rebalanced_portfolio(signal_df)

    backtest_df = run_vectorized_backtest(
        portfolio_df,
        initial_capital=INITIAL_CAPITAL,
    )

    metrics = calculate_performance_metrics(backtest_df)

    metrics["fold"] = fold_number
    metrics["train_start"] = train_start
    metrics["train_end"] = train_end
    metrics["test_start"] = test_start
    metrics["test_end"] = test_end

    return metrics


def main():
    df = pd.read_parquet(PREPARED_DATA_DIR / "all_features.parquet")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])

    min_date = df["date"].min()
    max_date = df["date"].max()

    results = []

    fold_number = 1
    train_start = min_date

    while True:
        train_end = train_start + pd.DateOffset(years=TRAIN_YEARS)
        test_start = train_end + pd.DateOffset(days=1)
        test_end = test_start + pd.DateOffset(months=TEST_MONTHS)

        if test_end > max_date:
            break

        print(f"Running fold {fold_number}...")

        metrics = run_fold(
            df=df,
            train_start=train_start,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
            fold_number=fold_number,
        )

        if metrics is not None:
            results.append(metrics)

        train_start = train_start + pd.DateOffset(months=TEST_MONTHS)
        fold_number += 1

    results_df = pd.DataFrame(results)

    output_dir = PREPARED_DATA_DIR.parent / "research"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "candidate_v2_walk_forward.csv"
    results_df.to_csv(output_path, index=False)

    print("\nCandidate V2 Walk-Forward Results")
    print("-" * 40)

    print(
        results_df[
            [
                "fold",
                "total_return",
                "annualized_return",
                "volatility",
                "sharpe_ratio",
                "max_drawdown",
            ]
        ].to_string(index=False)
    )

    print("\nAverage Metrics")
    print("-" * 40)

    for col in [
        "total_return",
        "annualized_return",
        "volatility",
        "sharpe_ratio",
        "max_drawdown",
    ]:
        print(f"{col}: {results_df[col].mean():.4f}")

    print("\nSaved:")
    print(output_path)


if __name__ == "__main__":
    main()