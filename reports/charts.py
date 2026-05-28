import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_equity_curve(backtest_df, output_path):
    plt.figure(figsize=(12, 6))
    plt.plot(backtest_df["date"], backtest_df["capital"])
    plt.title("Strategy Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_drawdown_curve(backtest_df, output_path):
    equity = backtest_df["capital"]
    running_max = equity.cummax()
    drawdown = (equity / running_max) - 1

    plt.figure(figsize=(12, 6))
    plt.plot(backtest_df["date"], drawdown)
    plt.title("Strategy Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_rolling_sharpe(
    backtest_df,
    output_path,
    return_col="portfolio_return",
    window=63,
):
    df = backtest_df.copy()

    df["rolling_sharpe"] = (
        df[return_col].rolling(window).mean()
        / df[return_col].rolling(window).std()
    ) * np.sqrt(252)

    plt.figure(figsize=(12, 6))
    plt.plot(df["date"], df["rolling_sharpe"])
    plt.axhline(0, linestyle="--")
    plt.title(f"{window}-Day Rolling Sharpe Ratio")
    plt.xlabel("Date")
    plt.ylabel("Rolling Sharpe")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()