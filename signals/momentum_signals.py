import pandas as pd


def build_cross_sectional_momentum_signal(
    df: pd.DataFrame,
    top_n: int = 5,
):
    signal_df = df.copy()

    signal_df = signal_df.sort_values(
        ["date", "mom_12m"],
        ascending=[True, False],
    )

    signal_df["signal_rank"] = (
        signal_df.groupby("date")["mom_12m"]
        .rank(ascending=False, method="first")
    )

    signal_df["long_signal"] = (
        signal_df["signal_rank"] <= top_n
    ).astype(int)

    signal_df["month"] = (
        pd.to_datetime(signal_df["date"])
        .dt.to_period("M")
    )

    monthly_signals = (
        signal_df.groupby(["month", "ticker"])
        .tail(1)
    )

    monthly_signals = monthly_signals[
        ["month", "ticker", "long_signal"]
    ]

    signal_df = signal_df.merge(
        monthly_signals,
        on=["month", "ticker"],
        suffixes=("", "_monthly"),
    )

    signal_df["long_signal"] = (
        signal_df["long_signal_monthly"]
    )

    signal_df = signal_df.drop(
        columns=["long_signal_monthly"]
    )

    return signal_df