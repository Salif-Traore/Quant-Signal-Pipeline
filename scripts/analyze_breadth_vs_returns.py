from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt

from configs.config import (
    PREPARED_DATA_DIR,
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


def main():

    features_df = pd.read_parquet(
        PREPARED_DATA_DIR / "all_features.parquet"
    )

    features_df["date"] = pd.to_datetime(
        features_df["date"]
    )

    features_df = features_df.sort_values(
        ["date", "ticker"]
    )

    features_df["positive_momentum"] = (
        features_df["mom_12m"] > 0
    ).astype(int)

    breadth = (
        features_df.groupby("date")["positive_momentum"]
        .mean()
        .reset_index()
    )

    breadth = breadth.rename(
        columns={
            "positive_momentum": "momentum_breadth"
        }
    )

    signal_df = (
        build_cross_sectional_momentum_signal(
            features_df
        )
    )

    portfolio_df = (
        build_monthly_rebalanced_portfolio(
            signal_df
        )
    )

    backtest_df = run_vectorized_backtest(
        portfolio_df
    )

    merged = backtest_df.merge(
        breadth,
        on="date",
        how="left",
    )

    merged["future_21d_return"] = (
        merged["portfolio_return"]
        .rolling(21)
        .sum()
        .shift(-21)
    )

    correlation = merged[
        ["momentum_breadth", "future_21d_return"]
    ].corr().iloc[0, 1]

    output_dir = (
        PREPARED_DATA_DIR.parent
        / "research"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    chart_path = (
        output_dir
        / "breadth_vs_future_returns.png"
    )

    plt.figure(figsize=(12, 6))

    plt.scatter(
        merged["momentum_breadth"],
        merged["future_21d_return"],
        alpha=0.5,
    )

    plt.title(
        "Momentum Breadth vs Future Strategy Returns"
    )

    plt.xlabel(
        "Momentum Breadth"
    )

    plt.ylabel(
        "Future 21-Day Strategy Return"
    )

    plt.tight_layout()

    plt.savefig(chart_path)

    plt.close()

    print("\nBreadth vs Returns Analysis")
    print("-" * 40)

    print(
        f"Correlation between breadth and future returns: "
        f"{correlation:.4f}"
    )

    print("\nSaved:")
    print(chart_path)


if __name__ == "__main__":
    main()