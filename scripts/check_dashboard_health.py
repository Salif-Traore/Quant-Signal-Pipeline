from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


FILES = {
    "backtest": PROJECT_ROOT / "data" / "backtests" / "portfolio_backtest_clean.parquet",
    "features": PROJECT_ROOT / "data" / "prepared" / "all_features.parquet",
    "metrics": PROJECT_ROOT / "data" / "backtests" / "performance_metrics.csv",
    "live_signals": PROJECT_ROOT / "data" / "live" / "latest_signals.csv",
    "paper_ledger": PROJECT_ROOT / "data" / "live" / "paper_trading_ledger.csv",
}


REQUIRED_COLUMNS = {
    "backtest": ["date", "capital", "portfolio_return"],
    "features": ["date", "ticker", "returns", "mom_1m", "vol_1m"],
    "live_signals": ["date", "ticker", "weight"],
    "paper_ledger": ["date", "ticker", "weight", "dollar_allocation", "paper_capital"],
}


def load_file(name, path):
    if not path.exists():
        raise FileNotFoundError(f"Missing {name}: {path}")

    if path.suffix == ".parquet":
        return pd.read_parquet(path)

    if path.suffix == ".csv":
        return pd.read_csv(path)

    raise ValueError(f"Unsupported file type: {path}")


def check_columns(name, df):
    required = REQUIRED_COLUMNS.get(name, [])

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"{name} missing columns: {missing}")


def main():
    print("\nDashboard Health Check")
    print("-" * 40)

    for name, path in FILES.items():
        print(f"Checking {name}...")

        df = load_file(name, path)

        if df.empty:
            raise ValueError(f"{name} is empty.")

        check_columns(name, df)

        print(f"OK: {name} rows={len(df):,}")

    print("\nChecking dashboard import...")

    import dashboard.app  # noqa: F401

    print("OK: dashboard imports successfully")

    print("\nAll dashboard health checks passed.")


if __name__ == "__main__":
    main()