from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PREPARED_DATA_DIR = DATA_DIR / "prepared"
BACKTEST_DATA_DIR = DATA_DIR / "backtests"

RESULTS_DIR = PROJECT_ROOT / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"

TICKERS = [
    "AAPL", "AGG", "BTC-USD", "EURUSD=X", "GLD",
    "IWM", "MSFT", "QQQ", "SLV", "SPY",
    "TLT", "USO", "XLF", "XLV", "^VIX"
]

PRICE_COL = "close"
DATE_COL = "date"
TICKER_COL = "ticker"

MOMENTUM_WINDOWS = {
    "1m": 21,
    "3m": 63,
    "6m": 126,
    "12m": 252,
}

VOL_WINDOWS = {
    "1m": 21,
    "3m": 63,
}

REBALANCE_FREQ = "M"
TOP_N = 5
INITIAL_CAPITAL = 100_000
TRANSACTION_COST_BPS = 5