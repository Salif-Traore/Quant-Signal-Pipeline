from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from configs.config import INITIAL_CAPITAL
from signals.momentum_signals import build_cross_sectional_momentum_signal
from portfolio.construction import build_monthly_rebalanced_portfolio
from backtesting.engine import run_vectorized_backtest
from reports.metrics import calculate_performance_metrics


COST_LEVELS = [
    0,
    5,
    10,
    25,
]


def main():
    features_df = pd.read_parquet(
        PROJECT_ROOT
        / "data"
        / "prepared"
        / "all_features.parquet"
    )

    signal_df = build_cross_sectional_momentum_signal(
        features_df
    )

    portfolio_df = build_monthly_rebalanced_portfolio(
        signal_df
    )

    results = []

    for cost in COST_LEVELS:

        backtest_df = run_vectorized_backtest(
            portfolio_df=portfolio_df,
            initial_capital=INITIAL_CAPITAL,
            transaction_cost_bps=cost,
        )

        metrics = calculate_performance_metrics(
            backtest_df
        )

        metrics["transaction_cost_bps"] = cost

        results.append(metrics)

    results_df = pd.DataFrame(results)

    results_df = results_df[
        [
            "transaction_cost_bps",
            "total_return",
            "annualized_return",
            "volatility",
            "sharpe_ratio",
            "max_drawdown",
        ]
    ]

    print("\nTransaction Cost Sweep")
    print("-" * 60)

    print(results_df.to_string(index=False))

    output_path = (
        PROJECT_ROOT
        / "data"
        / "research"
        / "transaction_cost_sweep.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        output_path,
        index=False,
    )

    print("\nSaved:")
    print(output_path)


if __name__ == "__main__":
    main()