import pandas as pd


def build_time_series_momentum_signal(
    df: pd.DataFrame,
    momentum_col: str = "mom_12m",
    vol_col: str = "vol_1m",
    top_n: int | None = None,
):
    signal_df = df.copy()

    signal_df = signal_df.sort_values(["date", "ticker"])

    signal_df["time_series_signal"] = (
        signal_df[momentum_col] > 0
    ).astype(int)

    signal_df["long_signal"] = signal_df["time_series_signal"]

    signal_df["signal_rank"] = (
        signal_df.groupby("date")[momentum_col]
        .rank(ascending=False, method="first")
    )

    signal_df["vol_rank"] = (
        signal_df.groupby("date")[vol_col]
        .rank(pct=True)
    )

    return signal_df