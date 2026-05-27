from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURE_FILE = PROJECT_ROOT / "data" / "prepared" / "all_features.parquet"
BACKTEST_DIR = PROJECT_ROOT / "data" / "backtests"

INITIAL_CAPITAL = 10000
TOP_N = 5

def main():
    BACKTEST_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(FEATURE_FILE)

    df = df.dropna(subset=["daily_return", "ts_momentum_12m"])

    df["selected"] = (
        df.groupby("Date")["ts_momentum_12m"]
        .rank(ascending=False, method="first") <= TOP_N
    )

    portfolio_returns = (
        df[df["selected"]]
        .groupby("Date")["daily_return"]
        .mean()
    )

    results = portfolio_returns.to_frame("portfolio_return")

    results["equity_curve"] = (
        INITIAL_CAPITAL * (1 + results["portfolio_return"]).cumprod()
    )

    results.to_parquet(
        BACKTEST_DIR / "portfolio_backtest.parquet"
    )

    print("Backtest complete.")
    print("Final capital:", round(results["equity_curve"].iloc[-1], 2))

if __name__ == "__main__":
    main()
