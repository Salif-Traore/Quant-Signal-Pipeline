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


def run_test(df, top_n):
    signal_df = build_cross_sectional_momentum_signal(
        df,
        top_n=top_n,
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
    metrics["top_n"] = top_n

    return metrics


def main():
    df = pd.read_parquet(PREPARED_DATA_DIR / "all_features.parquet")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])

    results = []

    for top_n in [3, 5, 7, 10]:
        print(f"Testing top_n={top_n}...")

        metrics = run_test(df, top_n)

        results.append(metrics)

    results_df = pd.DataFrame(results)

    output_dir = PREPARED_DATA_DIR.parent / "research"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "top_n_parameter_sweep.csv"

    results_df.to_csv(output_path, index=False)

    print("\nParameter Sweep Results")
    print("-" * 40)

    print(
        results_df[
            [
                "top_n",
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