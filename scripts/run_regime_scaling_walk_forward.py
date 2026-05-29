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

from signals.momentum_signals import (
    build_cross_sectional_momentum_signal,
)

from portfolio.construction import (
    build_monthly_rebalanced_portfolio,
)

from backtesting.engine import (
    run_vectorized_backtest,
)

from reports.metrics import (
    calculate_performance_metrics,
)


def compute_momentum_breadth(
    df,
    momentum_col="mom_1m",
):
    breadth = df.copy()

    breadth["positive_momentum"] = (
        breadth[momentum_col] > 0
    ).astype(int)

    breadth = (
        breadth.groupby("date")["positive_momentum"]
        .mean()
        .reset_index()
        .rename(
            columns={
                "positive_momentum": "momentum_breadth"
            }
        )
    )

    return breadth


def apply_exposure_scaling(
    portfolio_df,
    features_df,
    min_exposure=0.50,
    max_exposure=1.0,
):
    breadth = compute_momentum_breadth(features_df)

    df = portfolio_df.merge(
        breadth,
        on="date",
        how="left",
    )

    df["momentum_breadth"] = (
        df["momentum_breadth"]
        .fillna(0.5)
    )

    df["exposure_multiplier"] = (
        min_exposure
        + (
            (max_exposure - min_exposure)
            * df["momentum_breadth"]
        )
    )

    df["weight"] = (
        df["weight"]
        * df["exposure_multiplier"]
    )

    return df


def run_fold(
    train_df,
    test_df,
):
    signal_df = build_cross_sectional_momentum_signal(
        pd.concat([train_df, test_df])
    )

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = (
        build_monthly_rebalanced_portfolio(
            signal_df
        )
    )

    portfolio_df = apply_exposure_scaling(
        portfolio_df=portfolio_df,
        features_df=signal_df,
        min_exposure=0.50,
    )

    test_dates = test_df["date"].unique()

    portfolio_df = portfolio_df[
        portfolio_df["date"].isin(test_dates)
    ].copy()

    backtest_df = run_vectorized_backtest(
        portfolio_df,
        initial_capital=INITIAL_CAPITAL,
    )

    return backtest_df


def main():
    df = pd.read_parquet(
        PREPARED_DATA_DIR
        / "all_features.parquet"
    )

    df["date"] = pd.to_datetime(df["date"])

    unique_dates = sorted(df["date"].unique())

    train_size = 756
    test_size = 63

    results = []

    fold_backtests = []

    fold = 1

    for start_idx in range(
        0,
        len(unique_dates) - train_size - test_size,
        test_size,
    ):
        print(f"Running fold {fold}...")

        train_dates = unique_dates[
            start_idx : start_idx + train_size
        ]

        test_dates = unique_dates[
            start_idx + train_size :
            start_idx + train_size + test_size
        ]

        train_df = df[
            df["date"].isin(train_dates)
        ].copy()

        test_df = df[
            df["date"].isin(test_dates)
        ].copy()

        backtest_df = run_fold(
            train_df=train_df,
            test_df=test_df,
        )

        backtest_df["fold"] = fold

        fold_backtests.append(backtest_df)

        metrics = calculate_performance_metrics(
            backtest_df
        )

        metrics["fold"] = fold

        results.append(metrics)

        fold += 1

    results_df = pd.DataFrame(results)

    print("\nCandidate V3 Walk-Forward Results")
    print("-" * 50)

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
    print("-" * 50)

    avg_metrics = results_df[
        [
            "total_return",
            "annualized_return",
            "volatility",
            "sharpe_ratio",
            "max_drawdown",
        ]
    ].mean()

    for k, v in avg_metrics.items():
        print(f"{k}: {v:.4f}")

    output_dir = (
        PREPARED_DATA_DIR.parent
        / "research"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_path = (
        output_dir
        / "candidate_v3_walk_forward.csv"
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    all_backtests = pd.concat(
        fold_backtests,
        ignore_index=True,
    )

    backtest_path = (
        output_dir
        / "candidate_v3_backtests.parquet"
    )

    all_backtests.to_parquet(
        backtest_path,
        index=False,
    )

    print("\nSaved:")
    print(results_path)
    print(backtest_path)


if __name__ == "__main__":
    main()