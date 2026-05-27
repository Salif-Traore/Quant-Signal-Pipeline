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
from portfolio.construction import build_equal_weight_portfolio
from backtesting.engine import run_vectorized_backtest
from reports.metrics import (
    calculate_performance_metrics,
    calculate_benchmark_metrics,
    save_metrics_to_csv,
    calculate_turnover_statistics,
)
from reports.charts import plot_equity_curve, plot_drawdown_curve


def main():
    df = pd.read_parquet(PREPARED_DATA_DIR / "all_features.parquet")

    df = df[df["ticker"].isin(TRADABLE_TICKERS)]

    signal_df = build_cross_sectional_momentum_signal(df)

    portfolio_df = build_equal_weight_portfolio(signal_df)

    backtest_df = run_vectorized_backtest(
        portfolio_df,
        initial_capital=INITIAL_CAPITAL,
    )

    output_path = PREPARED_DATA_DIR.parent / "backtests" / "portfolio_backtest_clean.parquet"
    output_path.parent.mkdir(exist_ok=True)

    backtest_df.to_parquet(output_path)

    metrics = calculate_performance_metrics(backtest_df)

    benchmark_metrics = calculate_benchmark_metrics(
        df,
        benchmark_ticker="SPY",
        initial_capital=INITIAL_CAPITAL,
    )

    turnover_metrics = calculate_turnover_statistics(backtest_df)

    metrics_output = (
        PREPARED_DATA_DIR.parent
        / "backtests"
        / "performance_metrics.csv"
    )

    save_metrics_to_csv(
        metrics,
        benchmark_metrics,
        metrics_output,
    )

    charts_dir = PREPARED_DATA_DIR.parent / "backtests" / "charts"
    charts_dir.mkdir(exist_ok=True)

    equity_curve_path = charts_dir / "equity_curve.png"
    drawdown_curve_path = charts_dir / "drawdown_curve.png"

    plot_equity_curve(backtest_df, equity_curve_path)
    plot_drawdown_curve(backtest_df, drawdown_curve_path)

    print("\nStrategy Performance Metrics")
    print("-" * 30)

    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    print("\nSPY Benchmark Metrics")
    print("-" * 30)

    for k, v in benchmark_metrics.items():
        print(f"{k}: {v:.4f}")

    print("\nTurnover Metrics")
    print("-" * 30)

    for k, v in turnover_metrics.items():
        print(f"{k}: {v:.4f}")

    print("\nPipeline complete.")
    print(f"Saved backtest to: {output_path}")
    print(f"Saved metrics to: {metrics_output}")
    print(f"Saved equity curve to: {equity_curve_path}")
    print(f"Saved drawdown curve to: {drawdown_curve_path}")
    print(f"Final capital: {backtest_df['capital'].iloc[-1]:,.2f}")


if __name__ == "__main__":
    main()