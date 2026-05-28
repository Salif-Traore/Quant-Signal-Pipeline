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

from portfolio.construction import build_monthly_rebalanced_portfolio
from backtesting.engine import run_vectorized_backtest
from reports.metrics import calculate_performance_metrics


FOLD_3_TEST_START = "2024-11-30"
FOLD_3_TEST_END = "2025-02-28"


def build_candidate_signal(
    df,
    momentum_col="mom_1m",
    vol_col="vol_1m",
    vol_quantile=0.75,
    top_n=1,
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


def main():
    df = pd.read_parquet(PREPARED_DATA_DIR / "all_features.parquet")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])

    fold_df = df[
        (df["date"] >= FOLD_3_TEST_START)
        & (df["date"] <= FOLD_3_TEST_END)
    ].copy()

    signal_df = build_candidate_signal(fold_df)

    signal_df = signal_df[
        signal_df["ticker"].isin(TRADABLE_TICKERS)
    ].copy()

    portfolio_df = build_monthly_rebalanced_portfolio(signal_df)

    backtest_df = run_vectorized_backtest(
        portfolio_df,
        initial_capital=INITIAL_CAPITAL,
    )

    metrics = calculate_performance_metrics(backtest_df)

    selected_positions = portfolio_df[
        portfolio_df["weight"] > 0
    ].copy()

    selected_positions["position_return"] = (
        selected_positions["weight"]
        * selected_positions["returns"]
    )

    ticker_summary = (
        selected_positions.groupby("ticker")
        .agg(
            avg_weight=("weight", "mean"),
            total_position_return=("position_return", "sum"),
            avg_return=("returns", "mean"),
            days_held=("date", "count"),
            avg_vol_1m=("vol_1m", "mean"),
            avg_mom_1m=("mom_1m", "mean"),
        )
        .reset_index()
        .sort_values("total_position_return")
    )

    fold_df["positive_momentum"] = (
        fold_df["mom_1m"] > 0
    ).astype(int)

    breadth = (
        fold_df.groupby("date")["positive_momentum"]
        .mean()
        .reset_index()
        .rename(columns={"positive_momentum": "mom_1m_breadth"})
    )

    market_vol = (
        fold_df.groupby("date")["vol_1m"]
        .mean()
        .reset_index()
        .rename(columns={"vol_1m": "avg_universe_vol_1m"})
    )

    diagnostics = backtest_df.merge(
        breadth,
        on="date",
        how="left",
    ).merge(
        market_vol,
        on="date",
        how="left",
    )

    output_dir = PREPARED_DATA_DIR.parent / "research" / "fold3_failure"
    output_dir.mkdir(parents=True, exist_ok=True)

    ticker_summary_path = output_dir / "fold3_ticker_summary.csv"
    diagnostics_path = output_dir / "fold3_diagnostics.csv"
    equity_chart_path = output_dir / "fold3_equity_curve.png"
    breadth_chart_path = output_dir / "fold3_breadth_and_vol.png"

    ticker_summary.to_csv(ticker_summary_path, index=False)
    diagnostics.to_csv(diagnostics_path, index=False)

    plt.figure(figsize=(12, 6))
    plt.plot(diagnostics["date"], diagnostics["capital"])
    plt.title("Fold 3 Candidate Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Capital")
    plt.tight_layout()
    plt.savefig(equity_chart_path)
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.plot(
        diagnostics["date"],
        diagnostics["mom_1m_breadth"],
        label="1M Momentum Breadth",
    )
    plt.plot(
        diagnostics["date"],
        diagnostics["avg_universe_vol_1m"],
        label="Average 1M Volatility",
    )
    plt.title("Fold 3 Breadth and Volatility Diagnostics")
    plt.xlabel("Date")
    plt.legend()
    plt.tight_layout()
    plt.savefig(breadth_chart_path)
    plt.close()

    print("\nFold 3 Failure Analysis")
    print("-" * 40)

    print("\nFold 3 Metrics")
    print("-" * 20)
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    print("\nWorst Contributors")
    print("-" * 20)
    print(ticker_summary.head(10).to_string(index=False))

    print("\nBest Contributors")
    print("-" * 20)
    print(ticker_summary.tail(10).to_string(index=False))

    print("\nRegime Diagnostics")
    print("-" * 20)
    print(f"Average 1M momentum breadth: {diagnostics['mom_1m_breadth'].mean():.2%}")
    print(f"Minimum 1M momentum breadth: {diagnostics['mom_1m_breadth'].min():.2%}")
    print(f"Average universe 1M volatility: {diagnostics['avg_universe_vol_1m'].mean():.4f}")
    print(f"Maximum universe 1M volatility: {diagnostics['avg_universe_vol_1m'].max():.4f}")

    print("\nSaved:")
    print(ticker_summary_path)
    print(diagnostics_path)
    print(equity_chart_path)
    print(breadth_chart_path)


if __name__ == "__main__":
    main()