# Quant-Signal-Pipeline
## Quant Signal Pipeline

This project builds a modular pipeline to acquire, clean, validate, and prepare financial data for backtesting trading signals.

### Current Features

- ✅ Pulls 3 years of OHLCV data for 15 assets (stocks, ETFs, currencies, crypto, commodities)
- ✅ Saves data as efficient `.parquet` files
- ✅ Validates timestamp consistency and missing values
- ✅ Modular structure: base feature class, parquet loader, and backtest prep
