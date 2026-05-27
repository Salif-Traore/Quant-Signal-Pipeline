import pandas as pd


def normalize_price_dataframe(df: pd.DataFrame, ticker: str | None = None) -> pd.DataFrame:
    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            col[0].lower() if col[1] == "" else col[0].lower()
            for col in df.columns
        ]

    else:
        df.columns = [str(col).lower() for col in df.columns]

    if "date" not in df.columns:
        df = df.reset_index()

    df.columns = [str(col).lower() for col in df.columns]

    if "date" not in df.columns and "Date" in df.columns:
        df = df.rename(columns={"Date": "date"})

    if ticker is not None:
        df["ticker"] = ticker
    elif "original_ticker" in df.columns:
        df["ticker"] = df["original_ticker"]

    return df


def add_returns(df, price_col="close"):
    df = df.copy()
    df["returns"] = df[price_col].pct_change()
    return df


def add_momentum_features(df, price_col="close"):
    df = df.copy()

    df["mom_1m"] = df[price_col].pct_change(21)
    df["mom_3m"] = df[price_col].pct_change(63)
    df["mom_6m"] = df[price_col].pct_change(126)
    df["mom_12m"] = df[price_col].pct_change(252)

    return df


def add_volatility_features(df):
    df = df.copy()

    df["vol_1m"] = df["returns"].rolling(21).std() * (252 ** 0.5)
    df["vol_3m"] = df["returns"].rolling(63).std() * (252 ** 0.5)

    return df


def add_risk_adjusted_features(df):
    df = df.copy()

    df["vol_adj_mom_12m"] = df["mom_12m"] / df["vol_3m"]

    df["rolling_sharpe_3m"] = (
        df["returns"].rolling(63).mean()
        / df["returns"].rolling(63).std()
    ) * (252 ** 0.5)

    return df


def build_features(df, ticker: str | None = None):
    df = normalize_price_dataframe(df, ticker=ticker)
    df = df.sort_values("date")

    df = add_returns(df)
    df = add_momentum_features(df)
    df = add_volatility_features(df)
    df = add_risk_adjusted_features(df)

    return df