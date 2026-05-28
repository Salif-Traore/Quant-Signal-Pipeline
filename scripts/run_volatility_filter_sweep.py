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
    df,
    momentum_col="mom_1m",
    vol_col="vol_1m",
    vol_quantile=0.5,
    top_n=1,
):
    signal_df = df.copy()

    signal_df = signal_df.sort_values(
        ["date", "ticker"]
    )

    signal_df["vol_rank"] = (
        signal_df.groupby("date")[vol_col]
        .rank(pct=True)
    )

    signal_df = signal_df[
        signal_df["vol_rank"] <= vol_quantile
    ].copy()

    signal_df["signal_rank"] = (
        signal_df.groupby("date")[momentum_col]
        .rank(
            ascending=False,
            method="first",
        )
    )

    signal_df["long_signal"] = (
        signal_df["signal_rank"] <= top_n
    ).astype(int)

    return signal_df


def run_test(df, vol_quantile):
    signal_df = build_signal(
        df,
        vol_quantile=vol_quantile,
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

    metrics["vol_quantile"] = vol_quantile

    return metrics


def main():

    df = pd.read_parquet(
        PREPARED_DATA_DIR / "all_features.parquet"
    )

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(
        ["date", "ticker"]
    )

    results = []

    for vol_quantile in [0.25, 0.50, 0.75, 1.00]:

        print(
            f"Testing vol_quantile={vol_quantile}..."
        )

        metrics = run_test(
            df,
            vol_quantile=vol_quantile,
        )

        results.append(metrics)

    results_df = pd.DataFrame(results)

    output_dir = (
        PREPARED_DATA_DIR.parent
        / "research"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "volatility_filter_sweep.csv"
    )

    results_df.to_csv(
        output_path,
        index=False,
    )

    print("\nVolatility Filter Sweep")
    print("-" * 40)

    print(
        results_df[
            [
                "vol_quantile",
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