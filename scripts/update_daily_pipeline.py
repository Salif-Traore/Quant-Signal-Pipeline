from pathlib import Path
import subprocess
import sys
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[1]


SCRIPTS = [
    "download_data.py",
    "build_features.py",
    "run_pipeline.py",
    "generate_live_signals.py",
    "update_paper_trading_ledger.py",
]


def run_script(script_name: str):
    script_path = PROJECT_ROOT / "scripts" / script_name

    print("\n" + "=" * 60)
    print(f"Running: {script_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed.")


def get_latest_signal_date():
    latest_signals_path = (
        PROJECT_ROOT
        / "data"
        / "live"
        / "latest_signals.csv"
    )

    if not latest_signals_path.exists():
        return "Unknown"

    try:
        import pandas as pd

        signals = pd.read_csv(latest_signals_path)

        if signals.empty or "date" not in signals.columns:
            return "Unknown"

        latest_date = pd.to_datetime(signals["date"]).max()

        return latest_date.strftime("%Y-%m-%d")

    except Exception:
        return "Unknown"


def write_update_log():
    output_dir = PROJECT_ROOT / "data" / "live"
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = output_dir / "last_updated.txt"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_signal_date = get_latest_signal_date()

    log_path.write_text(
        (
            f"Last updated: {timestamp}\n"
            f"Latest signal date: {latest_signal_date}\n"
            f"Update source: scripts/update_daily_pipeline.py\n"
        ),
        encoding="utf-8",
    )

    print(f"\nWrote update log: {log_path}")


def main():
    print("\nStarting daily quant pipeline update...")

    for script_name in SCRIPTS:
        run_script(script_name)

    write_update_log()

    print("\nDaily pipeline update complete.")


if __name__ == "__main__":
    main()