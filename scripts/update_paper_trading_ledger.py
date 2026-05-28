from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


INITIAL_PAPER_CAPITAL = 100_000

LIVE_SIGNALS_PATH = (
    PROJECT_ROOT
    / "data"
    / "live"
    / "latest_signals.csv"
)

LEDGER_PATH = (
    PROJECT_ROOT
    / "data"
    / "live"
    / "paper_trading_ledger.csv"
)


def load_live_signals():
    if not LIVE_SIGNALS_PATH.exists():
        raise FileNotFoundError(
            f"Missing live signals file: {LIVE_SIGNALS_PATH}"
        )

    signals = pd.read_csv(LIVE_SIGNALS_PATH)

    if signals.empty:
        raise ValueError("Live signals file is empty.")

    signals["date"] = pd.to_datetime(signals["date"])

    return signals


def load_existing_ledger():
    if LEDGER_PATH.exists():
        ledger = pd.read_csv(LEDGER_PATH)
        ledger["date"] = pd.to_datetime(ledger["date"])
        return ledger

    return pd.DataFrame()


def main():
    signals = load_live_signals()
    ledger = load_existing_ledger()

    signal_date = signals["date"].max()

    todays_signals = signals[
        signals["date"] == signal_date
    ].copy()

    if not ledger.empty:
        existing_dates = pd.to_datetime(ledger["date"]).dt.date.unique()

        if signal_date.date() in existing_dates:
            print(
                f"Paper trading ledger already has entries for {signal_date.date()}."
            )
            print("No duplicate rows added.")
            return

        previous_capital = ledger["paper_capital"].iloc[-1]
    else:
        previous_capital = INITIAL_PAPER_CAPITAL

    todays_signals["paper_capital"] = previous_capital

    todays_signals["dollar_allocation"] = (
        todays_signals["weight"]
        * previous_capital
    )

    todays_signals["paper_position_id"] = (
        todays_signals["date"].dt.strftime("%Y-%m-%d")
        + "_"
        + todays_signals["ticker"]
    )

    todays_signals["paper_trade_type"] = "TARGET_WEIGHT"

    output_cols = [
        "date",
        "ticker",
        "weight",
        "dollar_allocation",
        "paper_capital",
        "paper_trade_type",
        "paper_position_id",
    ]

    optional_cols = [
        "mom_1m",
        "vol_1m",
        "returns",
        "signal_rank",
        "vol_rank",
    ]

    output_cols += [
        col for col in optional_cols
        if col in todays_signals.columns
    ]

    new_rows = todays_signals[output_cols].copy()

    updated_ledger = pd.concat(
        [ledger, new_rows],
        ignore_index=True,
    )

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    updated_ledger.to_csv(
        LEDGER_PATH,
        index=False,
    )

    print("\nPaper Trading Ledger Updated")
    print("-" * 40)
    print(f"Signal date: {signal_date.date()}")
    print(f"Paper capital: ${previous_capital:,.2f}")
    print(new_rows.to_string(index=False))

    print("\nSaved:")
    print(LEDGER_PATH)


if __name__ == "__main__":
    main()