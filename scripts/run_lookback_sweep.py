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


def build_signal(
    df: pd.DataFrame,
    momentum_col: str,
    top_n: int = 5,
):
    signal_df = df.copy()

    signal_df = signal_df.sort_values(["date", "ticker"])

    signal_df["signal_rank"] = (
        signal_df.groupby("date")[momentum_col]
        .rank(ascending=False, method="first")
    )

    signal_df["long_signal"] = (
        signal_df["signal_rank"] <= top_n
    ).astype(int)

    return signal_df


def run_test(df, momentum_col):
    signal_df = build_signal(
        df,
        momentum_col=momentum_col,
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
    metrics["momentum_col"] = momentum_col

    return metrics


def main():
    df = pd.read_parquet(PREPARED_DATA_DIR / "all_features.parquet")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])

    candidate_columns = [
        "mom_1m",
        "mom_3m",
        "mom_6m",
        "mom_12m",
    ]

    momentum_columns = [
        col for col in candidate_columns
        if col in df.columns
    ]

    print("\nAvailable momentum columns:")
    print(momentum_columns)

    results = []

    for col in momentum_columns:
        print(f"Testing {col}...")

        metrics = run_test(
            df,
            momentum_col=col,
        )

        results.append(metrics)

    results_df = pd.DataFrame(results)

    output_dir = PREPARED_DATA_DIR.parent / "research"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "lookback_sweep.csv"
    results_df.to_csv(output_path, index=False)

    print("\nLookback Sweep Results")
    print("-" * 40)

    print(
        results_df[
            [
                "momentum_col",
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