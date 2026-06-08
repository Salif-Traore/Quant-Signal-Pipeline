from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import numpy as np
import pandas as pd


BACKTEST_PATH = PROJECT_ROOT / "data" / "backtests" / "portfolio_backtest_clean.parquet"
FEATURES_PATH = PROJECT_ROOT / "data" / "prepared" / "all_features.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "research"


def build_momentum_factor(features_df):
    df = features_df.copy()

    df["mom_rank"] = df.groupby("date")["mom_12m"].rank(pct=True)

    top = df[df["mom_rank"] >= 0.70]
    bottom = df[df["mom_rank"] <= 0.30]

    top_returns = top.groupby("date")["returns"].mean()
    bottom_returns = bottom.groupby("date")["returns"].mean()

    factor = top_returns - bottom_returns
    factor.name = "momentum_factor"

    return factor.reset_index()


def build_volatility_factor(features_df):
    df = features_df.copy()

    df["vol_rank"] = df.groupby("date")["vol_3m"].rank(pct=True)

    low_vol = df[df["vol_rank"] <= 0.30]
    high_vol = df[df["vol_rank"] >= 0.70]

    low_vol_returns = low_vol.groupby("date")["returns"].mean()
    high_vol_returns = high_vol.groupby("date")["returns"].mean()

    factor = low_vol_returns - high_vol_returns
    factor.name = "low_vol_factor"

    return factor.reset_index()


def run_regression(y, X):
    X = X.copy()
    X.insert(0, "intercept", 1.0)

    y_values = y.values
    X_values = X.values

    betas = np.linalg.inv(X_values.T @ X_values) @ X_values.T @ y_values

    predictions = X_values @ betas
    residuals = y_values - predictions

    n = len(y_values)
    k = X_values.shape[1]

    residual_variance = (residuals.T @ residuals) / (n - k)

    covariance_matrix = residual_variance * np.linalg.inv(X_values.T @ X_values)
    standard_errors = np.sqrt(np.diag(covariance_matrix))

    t_stats = betas / standard_errors

    ss_total = ((y_values - y_values.mean()) ** 2).sum()
    ss_residual = (residuals ** 2).sum()

    r_squared = 1 - ss_residual / ss_total

    results = pd.DataFrame(
        {
            "factor": X.columns,
            "beta": betas,
            "t_stat": t_stats,
        }
    )

    return results, r_squared


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    backtest_df = pd.read_parquet(BACKTEST_PATH)
    features_df = pd.read_parquet(FEATURES_PATH)

    backtest_df["date"] = pd.to_datetime(backtest_df["date"])
    features_df["date"] = pd.to_datetime(features_df["date"])

    strategy_returns = backtest_df[
        ["date", "portfolio_return"]
    ].copy()

    spy_returns = (
        features_df[features_df["ticker"] == "SPY"]
        [["date", "returns"]]
        .rename(columns={"returns": "market_factor"})
    )

    momentum_factor = build_momentum_factor(features_df)
    volatility_factor = build_volatility_factor(features_df)

    factor_df = (
        strategy_returns
        .merge(spy_returns, on="date", how="inner")
        .merge(momentum_factor, on="date", how="inner")
        .merge(volatility_factor, on="date", how="inner")
        .dropna()
    )

    y = factor_df["portfolio_return"]

    X = factor_df[
        [
            "market_factor",
            "momentum_factor",
            "low_vol_factor",
        ]
    ]

    regression_results, r_squared = run_regression(y, X)

    output_path = OUTPUT_DIR / "factor_exposure_results.csv"
    factor_data_path = OUTPUT_DIR / "factor_exposure_dataset.csv"

    regression_results.to_csv(output_path, index=False)
    factor_df.to_csv(factor_data_path, index=False)

    print("\nFactor Exposure Analysis")
    print("-" * 40)

    print(regression_results.to_string(index=False))

    print("\nModel Fit")
    print("-" * 40)
    print(f"R-squared: {r_squared:.4f}")

    print("\nInterpretation Guide")
    print("-" * 40)
    print("market_factor: exposure to SPY daily returns")
    print("momentum_factor: exposure to high momentum minus low momentum assets")
    print("low_vol_factor: exposure to low volatility minus high volatility assets")

    print("\nSaved:")
    print(output_path)
    print(factor_data_path)


if __name__ == "__main__":
    main()