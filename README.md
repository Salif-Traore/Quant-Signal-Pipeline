# Quant-Signal-Pipeline
## Quant Signal Pipeline

This project builds a modular pipeline to acquire, clean, validate, and prepare financial data for backtesting trading signals.

### Current Features

- ✅ Pulls 3 years of OHLCV data for 15 assets (stocks, ETFs, currencies, crypto, commodities)
- ✅ Saves data as efficient `.parquet` files
- ✅ Validates timestamp consistency and missing values
- ✅ Modular structure: base feature class, parquet loader, and backtest prep
loaders/ — Parquet loader and other data source loaders.

features/ — Base feature class, time-series momentum, percent change, 12-month return, signal features.

backtests/ — Multi-ticker and single-ticker backtesting scripts.

scripts/ — Utility scripts for data validation, feature building, and backtest preparation.

✅ Generates performance metrics: cumulative returns, volatility, Sharpe ratio, drawdown, and turnover.

✅ Notebook examples for exploration, signal generation, and backtesting