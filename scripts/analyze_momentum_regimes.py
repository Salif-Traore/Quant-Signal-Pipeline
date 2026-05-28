from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt

from configs.config import PREPARED_DATA_DIR


def main():
    df = pd.read_parquet(
        PREPARED_DATA_DIR / "all_features.parquet"
    )

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(["date", "ticker"])

    df["positive_momentum"] = (
        df["mom_12m"] > 0
    ).astype(int)

    breadth = (
        df.groupby("date")["positive_momentum"]
        .mean()
        .reset_index()
    )

    breadth = breadth.rename(
        columns={
            "positive_momentum": "momentum_breadth"
        }
    )

    breadth["breadth_30d_ma"] = (
        breadth["momentum_breadth"]
        .rolling(30)
        .mean()
    )

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
        / "momentum_breadth.csv"
    )

    breadth.to_csv(
        output_path,
        index=False,
    )

    plt.figure(figsize=(14, 6))

    plt.plot(
        breadth["date"],
        breadth["momentum_breadth"],
        label="Daily Breadth",
        alpha=0.5,
    )

    plt.plot(
        breadth["date"],
        breadth["breadth_30d_ma"],
        label="30D Moving Average",
        linewidth=2,
    )

    plt.axhline(
        0.5,
        linestyle="--",
    )

    plt.title(
        "Momentum Breadth Through Time"
    )

    plt.xlabel("Date")
    plt.ylabel(
        "% of Stocks with Positive 12M Momentum"
    )

    plt.legend()

    chart_path = (
        output_dir
        / "momentum_breadth.png"
    )

    plt.tight_layout()

    plt.savefig(chart_path)

    plt.close()

    print("\nMomentum Regime Analysis Complete")
    print("-" * 40)

    print(
        f"Average breadth: "
        f"{breadth['momentum_breadth'].mean():.2%}"
    )

    print(
        f"Max breadth: "
        f"{breadth['momentum_breadth'].max():.2%}"
    )

    print(
        f"Min breadth: "
        f"{breadth['momentum_breadth'].min():.2%}"
    )

    print("\nSaved:")
    print(output_path)
    print(chart_path)


if __name__ == "__main__":
    main()