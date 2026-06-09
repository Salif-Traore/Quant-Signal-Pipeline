# Quant Signal Pipeline

A modular quantitative research platform for developing, testing, and evaluating systematic momentum-based investment strategies across multiple asset classes.

---

# Overview

This project started with a simple question:

**Can **systematic momentum strategies generate superior risk-adjusted returns relative to passive benchmarks?

Rather than attempting to predict markets through intuition, news interpretation, or subjective judgment, I built a repeatable quantitative research process capable of identifying opportunities, constructing portfolios, validating strategies, and generating live investment signals.

Over the course of this project, I built a complete end-to-end research platform in Python that:

* Creates a repeatable process for collecting, validating, and storing market data so research can be conducted on a reliable foundation.
* Transforms raw price data into momentum and risk features that can be tested as potential sources of investment signal.
* Converts research hypotheses into systematic trading signals that can be evaluated objectively.
* Constructs portfolios using explicit risk-allocation rules rather than discretionary position sizing.
* Simulates historical performance to measure how strategies would have behaved across different market environments.
* Evaluates strategy robustness through walk-forward testing and out-of-sample validation.
* Incorporates transaction costs to better approximate real-world implementation.
* Analyzes the drivers of performance to understand which signals and assets contributed to results.
* Produces live signals and research outputs through an interactive dashboard for ongoing monitoring.

---

# Strategy

The current production strategy is based on **cross-sectional momentum**.

Each month:

1. Assets are ranked using momentum signals.
2. The strongest assets are selected.
3. Portfolio weights are determined using inverse-volatility weighting.
4. The portfolio is rebalanced monthly.
5. Performance is tracked through a full backtesting framework.

The strategy seeks to allocate capital toward assets demonstrating the strongest relative strength while controlling risk through volatility-based position sizing.

### Research Universe

The portfolio trades across multiple asset classes:

* Equities
* ETFs
* Commodities
* Foreign Exchange
* Cryptocurrency
* Fixed Income

Example assets include:

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

* Cross-sectional momentum consistently outperformed the time-series momentum variants tested during this project.
* The strategy underperforms QQQ over the full period but does so with meaningfully lower volatility and drawdown.
* Adding positive-momentum filters improved signal quality in some environments but did not consistently improve overall portfolio performance.
* The upweighting of AGG and TLT introduces duration risk in rising rate environments — a known vulnerability of the strategy
* Regime-based exposure scaling reduced drawdowns during certain periods but underperformed the production strategy during walk-forward testing.
* The strategy remained profitable after incorporating realistic transaction cost assumptions, suggesting results were not solely driven by excessive trading.
* Performance was concentrated among a relatively small number of strong momentum winners rather than being evenly distributed across all holdings.
* Walk-forward validation produced results that were directionally consistent with in-sample testing, providing evidence that the strategy retained some robustness outside the original research period.
* Signal attribution identified GLD, AAPL, USO, and QQQ as the largest contributors to overall portfolio performance.

---

# Pipeline Architecture

Project Structure:

```text
configs/
features/
signals/
portfolio/
back testing/
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
Back testing
        ↓
Research Validation
        ↓
Dashboard
        ↓
Live Signals
```

---

# Feature Engineering

The feature pipeline generates:

* 1-Month Momentum
* 3-Month Momentum
* 6-Month Momentum
* 12-Month Momentum
* 1-Month Volatility
* 3-Month Volatility
* Volatility-Adjusted Momentum
* Rolling Sharpe Ratio

All features are stored in Parquet format for efficient research workflows.

---

# Research Framework

A major focus of this project was research and validation.

The following ideas were researched and tested:

### Cross-Sectional Momentum

The production strategy used throughout the pipeline.

### Time-Series Momentum (TSMOM)

A separate momentum framework tested against the production strategy.

### TSMOM Filters

Positive momentum filters were applied to determine whether signal quality could be improved.

### Regime-Based Exposure Scaling

Portfolio exposure was dynamically adjusted based on momentum breadth and market conditions.

### Walk-Forward Validation

Strategies were tested across rolling out-of-sample periods to reduce overfitting risk.

### Transaction Cost Analysis

Realistic transaction costs were incorporated to evaluate robustness under trading friction.

### Factor Exposure Analysis

Strategy returns were compared against market, momentum, and volatility factors.

### Signal Attribution

Historical performance was decomposed to identify which assets contributed most to returns.

---

# Current Features

## Data Pipeline

* Automated market data downloads
* Data validation
* Parquet storage
* Modular architecture

## Signal Layer

* Cross-sectional momentum ranking
* Asset selection framework
* Monthly signal generation

## Portfolio Construction

* Inverse-volatility weighting
* Risk-adjusted allocation
* Monthly rebalancing

## Backtesting

* Vectorized simulation engine
* Benchmark comparison
* Equity curve generation
* Drawdown analysis
* Transaction cost modeling

## Research Validation

* Parameter sweeps
* Walk-forward testing
* Regime analysis
* Factor exposure analysis
* Signal attribution analysis

## Dashboard

* Performance monitoring
* Walk-forward visualization
* Research results
* Live signals
* Paper trading ledger
* Signal attribution

---

# Current Performance

<img src="https://github.com/user-attachments/assets/9956753e-36c8-495a-8d10-ab7273e58654" />

<br><br>

<img src="https://github.com/user-attachments/assets/3cbd65a6-d9ac-4da4-bba6-5ead64451748" />


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

The complete research process is documented in:

```text
research/

01_cross_sectional_momentum.md
02_tsmom_research.md
03_tsmom_filter_research.md
04_regime_scaling_research.md
05_transaction_cost_analysis.md
06_signal_attribution_analysis.md
```

Each notebook includes:

* Hypothesis
* Methodology
* Results
* Conclusions

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

* Python
* Pandas
* NumPy
* Plotly
* Streamlit
* Parquet
* Git
* GitHub
* UV

---

# Future Improvements

Potential future research directions include:

* Multi-factor models
* Enhanced factor attribution
* Alternative portfolio construction techniques
* Additional asset universes
* Broker integration
* Automated cloud deployment
* Live paper trading automation

---

# Author

**Salif Traoré**

Economics & Finance
Syracuse University

This project demonstrates the ability to take an investment hypothesis from initial idea through data collection, feature engineering, portfolio construction, validation, and performance analysis. It reflects a research process focused on testing assumptions, evaluating evidence, and refining conclusions through systematic experimentation.
