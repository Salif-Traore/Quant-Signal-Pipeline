from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt

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


TRAIN_YEARS = 3
TEST_MONTHS = 6


def run_fold(
    df,
    train_start,
    train_end,
    test_start,
    test_end,
    fold_number,
):
    test_df = df[
        (df["date"] >= test_start)
        & (df["date"] <= test_end)
    ].copy()

    if len(test_df) == 0:
        return None

    signal_df = build_cross_sectional_momentum_signal(
        test_df
    )

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = (
        build_monthly_rebalanced_portfolio(
            signal_df
        )
    )

    backtest_df = run_vectorized_backtest(
        portfolio_df,
        initial_capital=INITIAL_CAPITAL,
    )

    metrics = calculate_performance_metrics(
        backtest_df
    )

    metrics["fold"] = fold_number
    metrics["train_start"] = train_start
    metrics["train_end"] = train_end
    metrics["test_start"] = test_start
    metrics["test_end"] = test_end

    return metrics, backtest_df


def main():
    df = pd.read_parquet(
        PREPARED_DATA_DIR / "all_features.parquet"
    )

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(
        ["date", "ticker"]
    )

    min_date = df["date"].min()
    max_date = df["date"].max()

    folds = []

    fold_backtests = []

    fold_number = 1

    train_start = min_date

    while True:
        train_end = (
            train_start
            + pd.DateOffset(years=TRAIN_YEARS)
        )

        test_start = (
            train_end
            + pd.DateOffset(days=1)
        )

        test_end = (
            test_start
            + pd.DateOffset(months=TEST_MONTHS)
        )

        if test_end > max_date:
            break

        result = run_fold(
            df=df,
            train_start=train_start,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
            fold_number=fold_number,
        )

        if result is not None:
            metrics, backtest_df = result

            folds.append(metrics)

            backtest_df["fold"] = fold_number

            fold_backtests.append(backtest_df)

            print("\nFold", fold_number)
            print("-" * 20)

            for k, v in metrics.items():

                if isinstance(v, float):
                    print(f"{k}: {v:.4f}")

                else:
                    print(f"{k}: {v}")

        train_start = (
            train_start
            + pd.DateOffset(months=TEST_MONTHS)
        )

        fold_number += 1

    walk_forward_results = pd.DataFrame(folds)

    output_dir = (
        PREPARED_DATA_DIR.parent
        / "backtests"
        / "walk_forward"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_path = (
        output_dir
        / "walk_forward_metrics.csv"
    )

    walk_forward_results.to_csv(
        metrics_path,
        index=False,
    )

    print("\nAverage Walk-Forward Metrics")
    print("-" * 30)

    metric_cols = [
        "total_return",
        "annualized_return",
        "volatility",
        "sharpe_ratio",
        "max_drawdown",
    ]

    for col in metric_cols:
        print(
            f"{col}: "
            f"{walk_forward_results[col].mean():.4f}"
        )

    if fold_backtests:

        combined = pd.concat(
            fold_backtests,
            ignore_index=True,
        )

        plt.figure(figsize=(12, 6))

        for fold in combined["fold"].unique():

            fold_df = combined[
                combined["fold"] == fold
            ]

            plt.plot(
                fold_df["date"],
                fold_df["capital"],
                label=f"Fold {fold}",
            )

        plt.title(
            "Walk-Forward Equity Curves"
        )

        plt.xlabel("Date")
        plt.ylabel("Capital")

        plt.legend()

        chart_path = (
            output_dir
            / "walk_forward_equity_curves.png"
        )

        plt.tight_layout()

        plt.savefig(chart_path)

        plt.close()

        print("\nSaved:")
        print(metrics_path)
        print(chart_path)


if __name__ == "__main__":
    main()