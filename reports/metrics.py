import pandas as pd
import numpy as np


def calculate_performance_metrics(
    portfolio_df: pd.DataFrame,
    return_col: str = "portfolio_return",
    capital_col: str = "capital",
):
    returns = portfolio_df[return_col].dropna()

    total_return = (
        portfolio_df[capital_col].iloc[-1]
        / portfolio_df[capital_col].iloc[0]
    ) - 1

    annualized_return = (
        (1 + total_return)
        ** (252 / len(portfolio_df))
    ) - 1

    volatility = (
        returns.std()
        * np.sqrt(252)
    )

    sharpe = (
        returns.mean()
        / returns.std()
    ) * np.sqrt(252)

    cumulative = (
        1 + returns
    ).cumprod()

    running_max = cumulative.cummax()

    drawdown = (
        cumulative / running_max
    ) - 1

    max_drawdown = drawdown.min()

    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "volatility": volatility,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
    }