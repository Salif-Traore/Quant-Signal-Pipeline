import pandas as pd


def run_vectorized_backtest(
    df: pd.DataFrame,
    return_col: str = "returns",
    weight_col: str = "weight",
    initial_capital: float = 100_000,
) -> pd.DataFrame:
    df = df.copy()

    df["next_return"] = (
        df.groupby("ticker")[return_col]
        .shift(-1)
    )

    df["weighted_return"] = (
        df[weight_col] * df["next_return"]
    )

    portfolio = (
        df.groupby("date")["weighted_return"]
        .sum()
        .reset_index()
    )

    portfolio["portfolio_return"] = portfolio["weighted_return"].fillna(0)

    portfolio["capital"] = (
        initial_capital
        * (1 + portfolio["portfolio_return"]).cumprod()
    )

    return portfolio