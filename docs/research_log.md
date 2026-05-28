\# Quant Signal Pipeline — Research Log



\## Project Overview



This project is a modular quantitative research pipeline focused on developing, testing, and improving systematic equity trading strategies using Python.



The goal of the project is to:

\- Build a professional quant research architecture

\- Develop momentum-based trading signals

\- Backtest strategies using vectorized portfolio simulation

\- Evaluate risk-adjusted performance

\- Iteratively improve portfolio construction and signal generation



\---



\# Initial Architecture



\## Core Components



The pipeline currently includes:



\- Modular repo structure

\- Config-driven architecture

\- Parquet-based data storage

\- Feature engineering pipeline

\- Momentum factor generation

\- Cross-sectional signal generation

\- Monthly portfolio rebalancing

\- Vectorized backtesting engine

\- Transaction cost modeling

\- Turnover analytics

\- Benchmark comparison

\- Performance reporting

\- Equity curve visualization

\- Drawdown analysis

\- Rolling Sharpe visualization



\---



\# Baseline Strategy



\## Strategy Definition



Initial strategy:



\- Cross-sectional momentum

\- 12-month momentum ranking

\- Monthly rebalance

\- Equal-weight portfolio

\- Long-only

\- Top-N ranked securities



\## Hypothesis



Stocks with the strongest trailing momentum may continue outperforming over intermediate horizons.



\---



\# Baseline Results



\## Performance Metrics



| Metric | Result |

|---|---|

| Total Return | 115.11% |

| Annualized Return | 19.20% |

| Volatility | 24.47% |

| Sharpe Ratio | 0.8396 |

| Max Drawdown | -22.89% |



\## Benchmark Comparison



\### SPY



| Metric | Result |

|---|---|

| Total Return | 70.12% |

| Sharpe Ratio | 1.0964 |



\### QQQ



| Metric | Result |

|---|---|

| Total Return | 98.17% |

| Sharpe Ratio | 1.1201 |



\## Observations



The baseline momentum strategy outperformed both SPY and QQQ on total return, but underperformed both benchmarks on risk-adjusted return (Sharpe ratio).



This suggested:

\- strong return generation

\- elevated volatility

\- opportunity for portfolio optimization



\---



\# Experiment 1 — Factor Combination Signals



\## Objective



Improve signal quality by combining:

\- raw momentum

\- volatility-adjusted momentum

\- rolling Sharpe signals



\## Hypothesis



Combining multiple factors may improve:

\- signal robustness

\- risk-adjusted returns

\- drawdown characteristics



\## Result



Performance deteriorated relative to the baseline strategy.



Observed:

\- lower total return

\- lower Sharpe ratio

\- worse drawdown behavior



\## Decision



Rejected.



The added complexity did not improve portfolio quality.



\---



\# Experiment 2 — Reduced Factor Combination



\## Objective



Test lighter factor blending:

\- 80% momentum

\- 20% risk-adjusted momentum



\## Result



Performance again deteriorated:

\- lower return

\- lower Sharpe ratio



\## Decision



Rejected.



Raw momentum remained the strongest standalone signal.



\---



\# Experiment 3 — Inverse Volatility Weighting



\## Objective



Improve portfolio construction by allocating:

\- larger weights to lower-volatility securities

\- smaller weights to higher-volatility securities



\## Hypothesis



Inverse-volatility weighting may:

\- reduce portfolio risk

\- improve Sharpe ratio

\- reduce drawdowns



\## Result



Performance improved meaningfully.



\### Updated Metrics



| Metric | Result |

|---|---|

| Total Return | 116.09% |

| Annualized Return | 19.32% |

| Volatility | 24.03% |

| Sharpe Ratio | 0.8551 |

| Max Drawdown | -20.35% |



\## Observations



This was the first modification that improved:

\- return

\- Sharpe ratio

\- volatility

\- drawdown simultaneously



Turnover increased modestly but remained acceptable.



\## Decision



Accepted.



Inverse-volatility weighting became part of the strategy baseline.



\---



\# Experiment 4 — SPY 200-Day Regime Filter



\## Objective



Reduce exposure during weak market environments.



Strategy only remained active when:

\- SPY > 200-day moving average



Otherwise:

\- portfolio moved to cash



\## Hypothesis



Trend-following market regime filters may reduce:

\- crash exposure

\- severe drawdowns



\## Result



Drawdowns improved materially, but returns deteriorated significantly.



\### Regime Filter Metrics



| Metric | Result |

|---|---|

| Total Return | 34.95% |

| Sharpe Ratio | 0.7110 |

| Max Drawdown | -10.77% |



\## Observations



The regime filter successfully reduced risk but removed too much upside participation.



\## Decision



Rejected.



The reduction in return and Sharpe ratio outweighed the drawdown improvement.



\---



\# Current Best Strategy



\## Final Accepted Strategy



Current best-performing configuration:



\- Cross-sectional 12-month momentum

\- Monthly rebalance

\- Long-only

\- Inverse-volatility weighting



\## Current Metrics



| Metric | Result |

|---|---|

| Total Return | 116.09% |

| Annualized Return | 19.32% |

| Volatility | 24.03% |

| Sharpe Ratio | 0.8551 |

| Max Drawdown | -20.35% |



\---



\# Current Research Priorities



Future planned improvements include:



\- Walk-forward testing

\- Out-of-sample validation

\- Benchmark-relative alpha analysis

\- Rolling beta analysis

\- Sector exposure controls

\- Factor neutralization

\- Transaction cost optimization

\- Streamlit dashboard

\- Long/short portfolio extensions

\- Prediction-market signal integration



\---



\# Lessons Learned



\## Key Findings



\- Simple momentum signals outperformed more complicated factor blends.

\- Portfolio construction materially impacts risk-adjusted performance.

\- Drawdown reduction techniques often reduce upside participation.

\- Incremental testing and controlled experimentation are critical.



\## Research Process



This project emphasized:

\- iterative experimentation

\- hypothesis-driven research

\- modular architecture design

\- performance attribution

\- disciplined rejection of weak ideas



The development process focused not only on maximizing returns, but also on improving:

\- robustness

\- maintainability

\- scalability

\- research transparency





\# Data Refresh \& Out-of-Sample Degradation



After updating the dataset through the current market period, strategy performance deteriorated materially.



Observed changes:

\- Sharpe ratio collapsed from 0.855 to 0.375

\- Max drawdown increased substantially

\- Momentum persistence weakened in newer market regimes



This highlighted the importance of:

\- out-of-sample validation

\- walk-forward testing

\- avoiding regime-specific overfitting



The updated results suggested that the strategy was less robust than originally believed.



\# Walk-Forward Testing Results



To evaluate robustness across changing market conditions, walk-forward testing was implemented using:



\- 3-year rolling training windows

\- 6-month out-of-sample testing windows



\## Average Results



| Metric | Result |

|---|---|

| Total Return | 18.07% |

| Annualized Return | 25.57% |

| Volatility | 20.48% |

| Sharpe Ratio | 1.2448 |

| Max Drawdown | -13.47% |



\## Observations



Performance varied meaningfully across folds:



\- Fold 1 and Fold 3 produced strong Sharpe ratios (>1.3)

\- Fold 2 weakened materially

\- No fold completely collapsed



This suggested:

\- momentum alpha remained present

\- strategy performance was regime dependent

\- robustness was stronger than implied by the single full-period backtest



Walk-forward testing significantly improved confidence in the strategy relative to the static backtest alone.

