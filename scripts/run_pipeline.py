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

    print("Pipeline complete.")
    print(f"Saved backtest to: {output_path}")
    print(f"Final capital: {backtest_df['capital'].iloc[-1]:,.2f}")


if __name__ == "__main__":
    main()