import pandas as pd


def build_monthly_rebalanced_portfolio(
    df: pd.DataFrame,
    signal_col: str = "long_signal",
) -> pd.DataFrame:
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"])

    df["month"] = df["date"].dt.to_period("M")

    rebalance_dates = (
        df.groupby("month")["date"]
        .max()
        .reset_index()
        .rename(columns={"date": "rebalance_date"})
    )

    df = df.merge(rebalance_dates, on="month", how="left")

    df["rebalance_signal"] = 0

    mask = df["date"] == df["rebalance_date"]
    df.loc[mask, "rebalance_signal"] = df.loc[mask, signal_col]

    df["held_signal_raw"] = df["rebalance_signal"].replace(0, pd.NA)

    df["held_signal"] = (
        df.groupby("ticker")["held_signal_raw"]
        .ffill()
        .fillna(0)
        .astype(int)
    )

    df["num_positions"] = (
        df.groupby("date")["held_signal"]
        .transform("sum")
    )

    df["weight"] = 0.0

    selected = df["held_signal"] == 1

    df.loc[selected, "weight"] = (
        1.0 / df.loc[selected, "num_positions"]
    )

    df["weight"] = df["weight"].fillna(0.0)

    return df