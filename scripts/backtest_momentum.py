# scripts/backtest_momentum.py

import pandas as pd

PROCESSED_DIR = "data/processed"
TICKER = "SPY"
INITIAL_CAPITAL = 10000

def run_backtest():
    df = pd.read_parquet(f"{PROCESSED_DIR}/{TICKER}.parquet")

    # Strategy: go long if yesterday's return > 0
    df["signal"] = (df["daily_return"].shift(1) > 0).astype(int)
    df["strategy_return"] = df["daily_return"] * df["signal"]

    # Calculate cumulative returns
    df["cumulative_strategy"] = (1 + df["strategy_return"]).cumprod()
    df["cumulative_buy_hold"] = (1 + df["daily_return"]).cumprod()

    final_strategy_value = INITIAL_CAPITAL * df["cumulative_strategy"].iloc[-1]
    final_buy_hold_value = INITIAL_CAPITAL * df["cumulative_buy_hold"].iloc[-1]

    print(f"📈 Final Strategy Value: ${final_strategy_value:.2f}")
    print(f"📊 Final Buy & Hold Value: ${final_buy_hold_value:.2f}")

if __name__ == "__main__":
    run_backtest()
