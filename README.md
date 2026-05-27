# Quant Signal Pipeline

A modular quantitative research platform for developing, testing, and evaluating systematic trading strategies across multiple asset classes.

## Overview

This project is designed as a hedge-fund-style research pipeline that:

- Downloads and processes market data
- Engineers momentum and volatility features
- Generates cross-sectional trading signals
- Constructs equal-weight portfolios
- Runs vectorized backtests
- Evaluates performance against SPY benchmark
- Produces charts and performance reports

The architecture emphasizes modularity, reproducibility, and scalable research workflows.

---

# Strategy

Current strategy implementation:

- Cross-sectional momentum
- Equal-weight portfolio construction
- Top-N ranked assets selected daily
- Benchmark comparison against SPY

Universe includes:

- Equities
- ETFs
- Commodities
- FX
- Crypto

---

# Project Architecture

```text
configs/
features/
signals/
portfolio/
backtesting/
reports/
scripts/
```

Pipeline flow:

```text
raw data
→ feature engineering
→ signal generation
→ portfolio construction
→ vectorized backtest
→ performance reporting
```

---

# Current Features

## Feature Engineering

- Rolling returns
- Volatility
- 1M momentum
- 3M momentum
- 6M momentum
- 12M momentum
- Volatility-adjusted momentum
- Rolling Sharpe ratio

## Signal Layer

- Cross-sectional momentum ranking
- Top-N asset selection
- Equal-weight position sizing

## Backtesting

- Vectorized portfolio simulation
- Benchmark comparison
- Portfolio equity tracking
- Drawdown analysis

## Reporting

- Performance metrics CSV export
- Equity curve generation
- Drawdown curve generation

---

# Current Performance

## Strategy Metrics

| Metric | Value |
|---|---|
| Total Return | 171.97% |
| Annualized Return | 25.79% |
| Volatility | 25.53% |
| Sharpe Ratio | 1.03 |
| Max Drawdown | -27.84% |

## SPY Benchmark

| Metric | Value |
|---|---|
| Total Return | 70.12% |
| Annualized Return | 19.52% |
| Volatility | 17.68% |
| Sharpe Ratio | 1.10 |
| Max Drawdown | -18.76% |

---

# Generated Outputs

The pipeline automatically generates:

```text
data/backtests/
├── portfolio_backtest_clean.parquet
├── performance_metrics.csv
└── charts/
    ├── equity_curve.png
    └── drawdown_curve.png
```

---

# Running The Pipeline

Run the complete research pipeline:

```bash
python scripts/run_pipeline.py
```

---

# Future Improvements

- Transaction costs
- Turnover analysis
- Monthly rebalancing
- Factor combinations
- Walk-forward testing
- Portfolio optimization
- Regime filters using VIX
- Live signal generation
- Streamlit dashboard
- Automated reporting

---

# Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Parquet
- Git
- GitHub

---

# Author

Salif Traore  
Economics & Finance — Syracuse University