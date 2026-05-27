import matplotlib.pyplot as plt


def plot_equity_curve(backtest_df, output_path):
    plt.figure(figsize=(10, 6))
    plt.plot(backtest_df["date"], backtest_df["capital"])
    plt.title("Strategy Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_drawdown_curve(backtest_df, output_path):
    df = backtest_df.copy()

    cumulative = df["capital"]
    running_max = cumulative.cummax()
    drawdown = (cumulative / running_max) - 1

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], drawdown)
    plt.title("Strategy Drawdown Curve")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()