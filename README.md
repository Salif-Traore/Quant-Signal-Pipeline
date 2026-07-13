**Disclaimer**
This project is for **educational and research purposes only**. It does not constitute real-world investment advice, financial advice, or a recommendation to buy or sell any securities or assets. 

Past performance is not indicative of future results. All backtested and simulated results shown are hypothetical and may not reflect real-world trading outcomes due to factors such as slippage, liquidity, changing market conditions, and execution costs.

Use this code and any signals at your own risk. The author assumes no responsibility for any financial losses incurred from the use of this software.

---

# Quant Signal Pipeline

A modular quantitative research platform for developing, testing, and evaluating systematic investment signals across multiple asset classes.

## Table of Contents

- [Overview](#overview)
- [Strategy](#strategy)
- [Research Universe](#research-universe)
- [Key Research Findings](#key-research-findings)
- [Pipeline Architecture](#pipeline-architecture)
- [Feature Engineering](#feature-engineering)
- [Research Framework](#research-framework)
- [Research Results](#research-results)
- [Walk-Forward Validation](#walk-forward-validation)
- [Research Notebooks](#research-notebooks)
- [Limitations](#limitations)
- [Lessons Learned](#lessons-learned)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Pipeline](#running-the-pipeline)
- [Technologies Used](#technologies-used)
- [Future Improvements](#future-improvements)
- [Author](#author)


---

# Overview

This project started with a simple question:

**Can systematic momentum signals survive rigorous testing once portfolio construction, transaction costs, and out-of-sample validation are introduced?**

Rather than relying on discretionary market forecasts, this project explores whether momentum-based investment signals can be transformed into a repeatable research process.

The platform includes data collection, feature engineering, signal generation, portfolio construction, backtesting, walk-forward validation, transaction cost modeling, performance attribution, and an interactive dashboard.

---

# Strategy

The current production strategy is based on **cross-sectional momentum**.

Each month:

1. Assets are ranked using momentum signals.
2. The highest-ranked assets become eligible for portfolio inclusion.
3. Portfolio weights are determined using inverse-volatility weighting.
4. The portfolio is rebalanced monthly.
5. Performance is tracked through a full backtesting framework.

The strategy seeks to allocate capital toward assets demonstrating the strongest relative strength while controlling risk through volatility-based position sizing.

---

# Research Universe

The portfolio trades across multiple asset classes:

- Equities
- ETFs
- Commodities
- Foreign Exchange
- Cryptocurrency
- Fixed Income

**Example assets include:**

```text
SPY - SPDR S&P 500 ETF
QQQ - Invesco QQQ (Nasdaq-100 ETF)
IWM - iShares Russell 2000 ETF
AAPL - Apple Inc.
MSFT - Microsoft Corp
GLD - SPDR Gold Shares
SLV - iShares Silver Trust
USO - United States Oil Fund
TLT - iShares 20+ Year Treasury Bond ETF
AGG - iShares Core U.S. Aggregate Bond ETF
BTC-USD - Bitcoin
EURUSD=X - Euro/ U.S. Dollar
```

---

# Key Research Findings

- Cross-sectional momentum produced stronger results than the time-series momentum variants tested during this project.
- Adding positive-momentum filters improved signal quality in some environments but did not consistently improve overall portfolio performance.
- Regime-based exposure scaling reduced drawdowns during certain periods but underperformed the production strategy during walk-forward testing.
- The strategy remained profitable after incorporating realistic transaction cost assumptions.
- Signal attribution identified GLD, AAPL, USO, and QQQ as the largest contributors to overall portfolio performance.

---

## Implementation Statistics

| Metric | Value |
|----------|----------|
| Rebalance Frequency | Monthly |
| Average Positions Held | 3.0 |
| Maximum Positions Held | 5 |
| Average Monthly Turnover | 15.47% |

A relatively modest turnover profile helped limit the impact of transaction costs during testing.

# Pipeline Architecture

Project Structure:

```text
configs/
features/
signals/
portfolio/
backtesting/
reports/
dashboard/
research/
scripts/
```

Research Pipeline:

```text
Data Collection
        ↓
Feature Engineering
        ↓
Signal Generation
        ↓
Portfolio Construction
        ↓
Backtesting
        ↓
Research Validation
        ↓
Dashboard
        ↓
Live Signals
```

---

# Feature Engineering

All features are calculated using only information that would have been available at the time of signal generation. This helps reduce look-ahead bias and better reflects how signals would have been generated in a live research environment.

The feature pipeline generates:

- 1-Month Momentum
- 3-Month Momentum
- 6-Month Momentum
- 12-Month Momentum
- 1-Month Volatility
- 3-Month Volatility
- Volatility-Adjusted Momentum
- Rolling Sharpe Ratio

All features are stored in Parquet format for efficient research workflows.

---

# Research Framework

A major focus of this project was research and validation.

The following ideas were implemented and tested:

- Cross-Sectional Momentum
- Time-Series Momentum (TSMOM)
- Positive Momentum Filters
- Regime-Based Exposure Scaling
- Walk-Forward Validation
- Transaction Cost Analysis
- Factor Exposure Analysis
- Signal Attribution

---

# Research Results

> Performance statistics are presented for research purposes only and should not be interpreted as evidence of future profitability.

## Strategy vs Benchmarks

The chart below compares the production strategy against SPY and QQQ over the full research period from July 2021 through May 2026.

<img src="https://github.com/user-attachments/assets/9956753e-36c8-495a-8d10-ab7273e58654" width="900" alt="Strategy vs SPY and QQQ equity curve">

        
The strategy produced a higher historical Sharpe ratio than SPY over the sample period while exhibiting lower volatility and drawdown. QQQ generated higher absolute returns during the same period.
        
*Portfolio growth from July 2021 through May 2026. Results are shown relative to SPY and QQQ benchmarks.*

## Walk-Forward Validation

<img src="https://github.com/user-attachments/assets/3cbd65a6-d9ac-4da4-bba6-5ead64451748" width="900" alt="Walk-Forward Validation results">

Average Walk-Forward Results:
• Annualized Return: 14.38%
• Sharpe Ratio: 1.03
• Maximum Drawdown: -4.67%
• Positive Fold Rate: 68.75%

Walk-forward validation was performed using rolling out-of-sample test periods. Positive Sharpe ratios across validation folds provide some evidence that performance was not entirely dependent on a single historical market environment, although the limited sample size warrants caution.

Production Strategy Results:

| Metric            | Value   |
| ----------------- | ------- |
| Total Return      | 66.91%  |
| Annualized Return | 10.62%  |
| Volatility        | 12.84%  |
| Sharpe Ratio      | 0.85    |
| Max Drawdown      | -21.72% |

SPY Benchmark:

| Metric            | Value   |
| ----------------- | ------- |
| Total Return      | 61.64%  |
| Annualized Return | 10.42%  |
| Volatility        | 16.37%  |
| Sharpe Ratio      | 0.69    |
| Max Drawdown      | -25.36% |

---

# Research Notebooks

- [Cross-Sectional Momentum Research](research/01_cross_sectional_momentum.md)
- [TSMOM Research](research/02_tsmom_research.md)
- [TSMOM Filter Research](research/03_tsmom_filter_research.md)
- [Regime Scaling Research](research/04_regime_scaling_research.md)
- [Transaction Cost Analysis](research/05_transaction_cost_analysis.md)
- [Signal Attribution Analysis](research/06_signal_attribution_analysis.md)

Each notebook includes:

* Hypothesis
* Methodology
* Results
* Conclusions

---

# Limitations

This project was built as a research and learning exercise rather than a production trading system.

Current limitations include:

- Relatively small asset universe
- Limited historical sample period
- Simplified transaction cost assumptions
- No market impact modeling
- No short-selling framework
- No live capital deployment history
- Reliance on daily data rather than intraday execution data

As a result, backtested results should be interpreted cautiously and may not reflect future performance.

---

# Lessons Learned

Several observations emerged during the research process:

- Portfolio construction can matter as much as signal generation.
- Strong in-sample performance frequently weakens during walk-forward testing.
- Transaction costs can materially impact strategy viability.
- Risk management decisions often have a larger effect on outcomes than individual signals.
- Robust research processes are more valuable than individual backtests.
  
Many ideas that appeared attractive initially were ultimately rejected after additional testing, reinforcing the importance of out-of-sample validation.

---

# Prerequisites
  
- Python 3.11+
- UV package manager

Install UV:

```bash
pip install uv
```

For additional installation options, see:
https://docs.astral.sh/uv/

---

# Installation

Clone the repository:

```bash
git clone https://github.com/Salif-Traore/Quant-Signal-Pipeline.git
cd quant-signal-pipeline
```

Create a virtual environment using UV:

```bash
uv venv
```

Activate the virtual environment:

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**

```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install project dependencies:

```bash
uv sync
```

Verify the installation:

```bash
uv run python --version
```

You should now be ready to run the research pipeline and dashboard. 

---

# Running The Pipeline

Update Data:

```bash
uv run python scripts/download_data.py
```

Build Features:

```bash
uv run python scripts/build_features.py
```

Run Backtest:

```bash
uv run python scripts/run_pipeline.py
```

Walk-Forward Validation:

```bash
uv run python scripts/run_walk_forward.py
```

Signal Attribution:

```bash
uv run python scripts/signal_attribution.py
```

Launch Dashboard:

```bash
uv run streamlit run dashboard/app.py
```

---

# Technologies Used

| Category | Tools |
|-----------|-----------|
| Programming | Python |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| Dashboarding | Streamlit |
| Data Storage | Parquet |
| Version Control | Git, GitHub |
| Environment Management | UV |

---

# Future Improvements

Potential future research directions include:

- Multi-factor models
- Enhanced factor attribution
- Alternative portfolio construction techniques
- Additional asset universes
- Broker integration
- Automated cloud deployment
- Live paper trading automation

---

# Author

**Salif Traoré**  
Economics Major & Finance Minor  
Syracuse University  

Built as an independent research project to learn systematic investment research, portfolio construction, and quantitative analysis.

---

## License

This project is licensed under the [MIT License](LICENSE).
