import pandas as pd


def run_vectorized_backtest(
    portfolio_df: pd.DataFrame,
    return_col: str = "returns",
    weight_col: str = "weight",
    initial_capital: float = 100_000,
    transaction_cost_bps: float = 10,
):
    df = portfolio_df.copy()

    df = df.sort_values(["ticker", "date"])

    df["next_return"] = (
        df.groupby("ticker")[return_col]
        .shift(-1)
    )

    df["weighted_return"] = (
        df[weight_col] * df["next_return"]
    )

    portfolio_returns = (
        df.groupby("date")["weighted_return"]
        .sum()
        .reset_index()
    )

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
        .reset_index()
    )

    turnover.columns = ["date", "turnover"]

    portfolio_returns = portfolio_returns.merge(
        turnover,
        on="date",
        how="left",
    )

    portfolio_returns["transaction_cost"] = (
        portfolio_returns["turnover"]
        * (transaction_cost_bps / 10000)
    )

    portfolio_returns["gross_return"] = (
        portfolio_returns["weighted_return"]
    )

    portfolio_returns["portfolio_return"] = (
        portfolio_returns["gross_return"]
        - portfolio_returns["transaction_cost"]
    )

    portfolio_returns["capital"] = (
        initial_capital
        * (1 + portfolio_returns["portfolio_return"].fillna(0)).cumprod()
    )

    return portfolio_returns