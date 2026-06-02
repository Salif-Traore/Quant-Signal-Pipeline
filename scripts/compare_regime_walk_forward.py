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


TRAIN_SIZE = 756
TEST_SIZE = 63


STRATEGIES = [
    {
        "strategy_name": "production_cross_sectional",
        "min_exposure": 1.00,
    },
    {
        "strategy_name": "regime_scaling_070",
        "min_exposure": 0.70,
    },
    {
        "strategy_name": "regime_scaling_060",
        "min_exposure": 0.60,
    },
]


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
    if min_exposure == 1.0:
        portfolio_df = portfolio_df.copy()
        portfolio_df["momentum_breadth"] = 1.0
        portfolio_df["exposure_multiplier"] = 1.0
        return portfolio_df

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


def run_single_fold(
    train_df,
    test_df,
    min_exposure,
):
    combined_df = pd.concat(
        [train_df, test_df],
        ignore_index=True,
    )

    signal_df = build_cross_sectional_momentum_signal(combined_df)

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = build_monthly_rebalanced_portfolio(signal_df)

    portfolio_df = apply_exposure_scaling(
        portfolio_df=portfolio_df,
        features_df=signal_df,
        min_exposure=min_exposure,
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


def run_strategy_walk_forward(
    df,
    strategy_name,
    min_exposure,
):
    unique_dates = sorted(df["date"].unique())

    results = []
    fold_backtests = []

    fold = 1

    for start_idx in range(
        0,
        len(unique_dates) - TRAIN_SIZE - TEST_SIZE,
        TEST_SIZE,
    ):
        print(
            f"Running {strategy_name} | fold {fold} | min_exposure={min_exposure:.2f}"
        )

        train_dates = unique_dates[
            start_idx : start_idx + TRAIN_SIZE
        ]

        test_dates = unique_dates[
            start_idx + TRAIN_SIZE :
            start_idx + TRAIN_SIZE + TEST_SIZE
        ]

        train_df = df[df["date"].isin(train_dates)].copy()
        test_df = df[df["date"].isin(test_dates)].copy()

        backtest_df = run_single_fold(
            train_df=train_df,
            test_df=test_df,
            min_exposure=min_exposure,
        )

        backtest_df["fold"] = fold
        backtest_df["strategy_name"] = strategy_name
        backtest_df["min_exposure"] = min_exposure

        fold_backtests.append(backtest_df)

        metrics = calculate_performance_metrics(backtest_df)

        metrics["fold"] = fold
        metrics["strategy_name"] = strategy_name
        metrics["min_exposure"] = min_exposure

        results.append(metrics)

        fold += 1

    results_df = pd.DataFrame(results)

    backtests_df = pd.concat(
        fold_backtests,
        ignore_index=True,
    )

    return results_df, backtests_df


def main():
    df = pd.read_parquet(PREPARED_DATA_DIR / "all_features.parquet")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])

    all_results = []
    all_backtests = []

    for strategy in STRATEGIES:
        results_df, backtests_df = run_strategy_walk_forward(
            df=df,
            strategy_name=strategy["strategy_name"],
            min_exposure=strategy["min_exposure"],
        )

        all_results.append(results_df)
        all_backtests.append(backtests_df)

    comparison_df = pd.concat(
        all_results,
        ignore_index=True,
    )

    comparison_backtests_df = pd.concat(
        all_backtests,
        ignore_index=True,
    )

    leaderboard = (
        comparison_df.groupby(
            ["strategy_name", "min_exposure"]
        )
        .agg(
            avg_total_return=("total_return", "mean"),
            avg_annualized_return=("annualized_return", "mean"),
            avg_volatility=("volatility", "mean"),
            avg_sharpe=("sharpe_ratio", "mean"),
            avg_max_drawdown=("max_drawdown", "mean"),
            positive_folds=("total_return", lambda x: (x > 0).sum()),
            total_folds=("total_return", "count"),
        )
        .reset_index()
    )

    leaderboard["positive_fold_rate"] = (
        leaderboard["positive_folds"]
        / leaderboard["total_folds"]
    )

    leaderboard = leaderboard.sort_values(
        "avg_sharpe",
        ascending=False,
    )

    output_dir = PREPARED_DATA_DIR.parent / "research"
    output_dir.mkdir(parents=True, exist_ok=True)

    comparison_path = output_dir / "regime_walk_forward_comparison.csv"
    leaderboard_path = output_dir / "regime_walk_forward_leaderboard.csv"
    backtests_path = output_dir / "regime_walk_forward_backtests.parquet"

    comparison_df.to_csv(comparison_path, index=False)
    leaderboard.to_csv(leaderboard_path, index=False)
    comparison_backtests_df.to_parquet(backtests_path, index=False)

    print("\nRegime Walk-Forward Leaderboard")
    print("-" * 70)

    print(
        leaderboard[
            [
                "strategy_name",
                "min_exposure",
                "avg_total_return",
                "avg_annualized_return",
                "avg_volatility",
                "avg_sharpe",
                "avg_max_drawdown",
                "positive_fold_rate",
            ]
        ].to_string(index=False)
    )

    print("\nSaved:")
    print(comparison_path)
    print(leaderboard_path)
    print(backtests_path)


if __name__ == "__main__":
    main()