import pandas as pd


def calculate_turnover(
    portfolio_df: pd.DataFrame,
    weight_col: str = "weight",
):
    df = portfolio_df.copy()

    df = df.sort_values(["ticker", "date"])

    df["prev_weight"] = (
        df.groupby("ticker")[weight_col]
        .shift(1)
        .fillna(0)
    )

    df["weight_change"] = (
        df[weight_col] - df["prev_weight"]
    ).abs()

    turnover = (
        df.groupby("date")["weight_change"]
        .sum()
    )

    turnover = turnover.reset_index()
    turnover.columns = ["date", "turnover"]

    return turnover