import pandas as pd
import numpy as np


def build_equal_weight_portfolio(
    df: pd.DataFrame,
    signal_col: str = "long_signal",
) -> pd.DataFrame:
    df = df.copy()

    df["num_positions"] = (
        df.groupby("date")[signal_col]
        .transform("sum")
    )

    df["weight"] = 0.0

    selected = df[signal_col] == 1

    df.loc[selected, "weight"] = (
        1.0 / df.loc[selected, "num_positions"]
    )

    df["weight"] = df["weight"].fillna(0.0)

    return df


def build_monthly_rebalanced_portfolio(
    df: pd.DataFrame,
    signal_col: str = "long_signal",
    vol_col: str = "vol_1m",
) -> pd.DataFrame:
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "ticker"])
    df["month"] = df["date"].dt.to_period("M")

    rebalance_dates = (
        df.groupby("month")["date"]
        .max()
        .reset_index()
        .rename(columns={"date": "rebalance_date"})
    )

    df = df.merge(
        rebalance_dates,
        on="month",
        how="left",
    )

    df["rebalance_weight"] = np.nan

    rebalance_mask = df["date"] == df["rebalance_date"]

    selected = (
        rebalance_mask
        & (df[signal_col] == 1)
    )

    df["inv_vol"] = 0.0

    df.loc[selected, "inv_vol"] = (
        1.0 / df.loc[selected, vol_col]
    )

    df["inv_vol"] = df["inv_vol"].replace(
        [np.inf, -np.inf],
        np.nan,
    )

    df["inv_vol"] = df["inv_vol"].fillna(0.0)

    df.loc[selected, "rebalance_weight"] = (
        df.loc[selected, "inv_vol"]
        / df.loc[selected]
        .groupby("date")["inv_vol"].transform("sum")
    )

    df.loc[
        rebalance_mask & (df[signal_col] == 0),
        "rebalance_weight",
    ] = 0.0

    df["rebalance_weight"] = pd.to_numeric(
        df["rebalance_weight"],
        errors="coerce",
    )

    df["weight"] = (
        df.sort_values(["ticker", "date"])
        .groupby("ticker")["rebalance_weight"]
        .ffill()
        .fillna(0.0)
        .astype(float)
    )

    df["weight"] = df["weight"].fillna(0.0)

    return df