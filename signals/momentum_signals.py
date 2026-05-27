import pandas as pd


def build_cross_sectional_momentum_signal(
    df: pd.DataFrame,
    signal_col: str = "mom_12m",
    top_n: int = 5,
) -> pd.DataFrame:

    df = df.copy()

    df["signal_rank"] = (
        df.groupby("date")[signal_col]
        .rank(ascending=False, method="first")
    )

    df["long_signal"] = (
        df["signal_rank"] <= top_n
    ).astype(int)

    return df


def build_vol_adjusted_momentum_signal(
    df: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:

    df = df.copy()

    df["vol_adj_rank"] = (
        df.groupby("date")["vol_adj_mom_12m"]
        .rank(ascending=False, method="first")
    )

    df["vol_adj_long_signal"] = (
        df["vol_adj_rank"] <= top_n
    ).astype(int)

    return df