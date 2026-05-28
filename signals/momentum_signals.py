import pandas as pd


def build_cross_sectional_momentum_signal(
    df: pd.DataFrame,
    top_n: int = 3,
    momentum_col: str = "mom_1m",
    vol_col: str = "vol_1m",
    vol_quantile: float = 0.75,
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