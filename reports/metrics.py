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

    annualized_return = ((1 + total_return) ** (252 / len(portfolio_df))) - 1

    volatility = returns.std() * np.sqrt(252)

    sharpe = (returns.mean() / returns.std()) * np.sqrt(252)

    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative / running_max) - 1
    max_drawdown = drawdown.min()

    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "volatility": volatility,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
    }


def calculate_benchmark_metrics(
    features_df: pd.DataFrame,
    benchmark_tickers: list[str],
    initial_capital: float = 100_000,
):
    benchmark_results = {}

    for ticker in benchmark_tickers:
        benchmark = features_df[features_df["ticker"] == ticker].copy()
        benchmark = benchmark.sort_values("date")

        benchmark["benchmark_return"] = benchmark["returns"].fillna(0)

        benchmark["benchmark_capital"] = (
            initial_capital
            * (1 + benchmark["benchmark_return"]).cumprod()
        )

        metrics = calculate_performance_metrics(
            benchmark,
            return_col="benchmark_return",
            capital_col="benchmark_capital",
        )

        benchmark_results[ticker] = metrics

    return benchmark_results


def save_metrics_to_csv(
    strategy_metrics: dict,
    benchmark_metrics: dict,
    output_path,
):
    rows = []

    for metric_name, strategy_value in strategy_metrics.items():
        row = {
            "metric": metric_name,
            "strategy": strategy_value,
        }

        for benchmark_name, benchmark_data in benchmark_metrics.items():
            row[f"benchmark_{benchmark_name.lower()}"] = benchmark_data.get(
                metric_name
            )

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)


def calculate_turnover_statistics(
    portfolio_df: pd.DataFrame,
):
    avg_turnover = portfolio_df["turnover"].mean()
    annualized_turnover = avg_turnover * 252

    return {
        "average_daily_turnover": avg_turnover,
        "annualized_turnover": annualized_turnover,
    }