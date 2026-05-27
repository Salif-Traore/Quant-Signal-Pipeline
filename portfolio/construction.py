import pandas as pd


def build_equal_weight_portfolio(
    df: pd.DataFrame,
    signal_col: str = "long_signal",
) -> pd.DataFrame:
    df = df.copy()

    df["num_positions"] = (
        df.groupby("date")[signal_col]
        .transform("sum")
    )

    df["weight"] = 0.0

    mask = df[signal_col] == 1

    df.loc[mask, "weight"] = (
        1.0 / df.loc[mask, "num_positions"]
    )

    df["weight"] = df["weight"].fillna(0.0)

    return df