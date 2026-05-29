\# Quant Signal Pipeline White Paper



\## 1. Abstract



This project develops a modular quantitative research pipeline for testing equity and cross-asset momentum strategies. The final framework includes automated data ingestion, feature engineering, signal generation, portfolio construction, vectorized backtesting, walk-forward validation, live signal generation, and an interactive Streamlit dashboard.



The final selected strategy uses short-term momentum, volatility filtering, and inverse-volatility weighting to improve risk-adjusted returns relative to earlier baseline approaches.



\---



\## 2. Research Objective



The objective of this project was to build a systematic trading research framework capable of:



\- Downloading and refreshing market data

\- Engineering momentum and volatility features

\- Generating cross-sectional trading signals

\- Constructing portfolios using rule-based weighting

\- Backtesting performance against benchmarks

\- Testing robustness through parameter sweeps and walk-forward validation

\- Producing live signals

\- Displaying results in a deployed dashboard



\---



\## 3. Initial Strategy Hypothesis



The original hypothesis was that assets with strong trailing momentum would continue to outperform over intermediate horizons.



The initial baseline strategy used:



\- 12-month momentum

\- top-5 asset selection

\- monthly rebalancing

\- long-only exposure

\- inverse-volatility weighting



\---



\## 4. Baseline Results



The early baseline showed promising results, but performance weakened after the dataset was refreshed with more recent market data.



This revealed an important research lesson: strong in-sample performance can deteriorate once the market regime changes or the sample expands.



\---



\## 5. Research Iteration Trail



\### 5.1 12-Month Momentum Baseline



The initial strategy ranked assets by 12-month momentum and selected the top assets.



Result:

\- Generated positive returns

\- Struggled with drawdowns after data refresh

\- Sharpe ratio weakened in the expanded dataset



Decision:

\- Retained as the first benchmark strategy, but not final.



\---



\### 5.2 Factor Combination Signals



The strategy tested combinations of:



\- raw momentum

\- volatility-adjusted momentum

\- rolling Sharpe



Result:

\- Added complexity

\- Did not improve performance

\- Reduced robustness



Decision:

\- Rejected.



\---



\### 5.3 Inverse Volatility Weighting



Portfolio construction was upgraded from equal-weighting to inverse-volatility weighting.



Result:

\- Improved risk control

\- Reduced drawdowns in some periods

\- Became part of the portfolio construction framework



Decision:

\- Accepted.



\---



\### 5.4 SPY 200-Day Regime Filter



A binary market regime filter was tested:



\- risk-on when SPY traded above its 200-day moving average

\- risk-off otherwise



Result:

\- Reduced drawdowns

\- Removed too much upside

\- Lowered total return and Sharpe ratio



Decision:

\- Rejected.



\---



\### 5.5 Momentum Breadth Analysis



Momentum breadth measured the percentage of assets with positive momentum.



Result:

\- Breadth had a small positive relationship with future strategy returns

\- Suggested the strategy was regime-sensitive

\- Helped explain periods of stronger and weaker momentum performance



Decision:

\- Used as a diagnostic tool, not as a final trading rule.



\---



\### 5.6 Breadth-Aware Exposure Scaling



The portfolio tested exposure scaling based on momentum breadth.



Result:

\- Reduced exposure during weak regimes

\- Lowered volatility

\- Reduced returns too aggressively



Decision:

\- Rejected as a trading rule.



\---



\### 5.7 Lookback Optimization



Momentum lookbacks were tested across:



\- 1-month momentum

\- 3-month momentum

\- 6-month momentum

\- 12-month momentum



Result:

\- 1-month momentum produced the strongest results in the refreshed dataset



Decision:

\- Accepted for the final candidate strategy.



\---



\### 5.8 Top-N Parameter Sweep



Different portfolio concentration levels were tested.



Result:

\- Very concentrated portfolios performed strongly but had unstable drawdowns

\- top-1 was too concentrated

\- top-3 improved balance between return and risk



Decision:

\- top-3 selected for final candidate strategy.



\---



\### 5.9 Volatility Filter



The final candidate applied a volatility filter, removing the highest-volatility assets before ranking by 1-month momentum.



Result:

\- Improved Sharpe ratio

\- Reduced drawdowns

\- Improved robustness



Decision:

\- Accepted.



\---



\## 6. Final Strategy



The final selected strategy uses:



\- 1-month momentum

\- top-3 ranked assets

\- 75th percentile volatility filter

\- inverse-volatility weighting

\- long-only exposure



\---



\## 7. Final Backtest Results



Final production strategy metrics:



| Metric | Result |

|---|---|

| Total Return | 67.00% |

| Annualized Return | 10.63% |

| Volatility | 12.84% |

| Sharpe Ratio | 0.8514 |

| Max Drawdown | -21.72% |



\---



\## 8. Benchmark Comparison



The strategy was compared against:



\- SPY

\- QQQ



The final strategy improved risk-adjusted performance relative to SPY and materially reduced volatility and drawdown compared with earlier versions of the strategy.



\---



\## 9. Walk-Forward Validation



Walk-forward testing was used to evaluate robustness across different market regimes.



The most robust candidate used:



\- 3-year training windows

\- 3-month testing windows

\- 1-month momentum

\- top-3 selection

\- volatility filtering



This showed stronger and more stable out-of-sample behavior than earlier versions.



\---



\## 10. Live Signal System



The project includes a live signal generation script that outputs the most recent recommended portfolio weights.



Latest live signal example:



| Ticker | Weight |

|---|---|

| QQQ | 37.08% |

| AAPL | 34.03% |

| IWM | 28.89% |



\---



\## 11. Dashboard and Deployment



The project includes a deployed Streamlit dashboard with:



\- performance metrics

\- benchmark overlays

\- rolling Sharpe

\- rolling alpha and beta

\- walk-forward results

\- parameter sweep results

\- regime diagnostics

\- current holdings

\- live signals

\- Monte Carlo simulation

\- downloadable CSVs



\---



\## 12. Automation



A daily update pipeline was added to refresh:



\- market data

\- features

\- backtest results

\- live signals

\- update logs



This allows the project to function as a living research system rather than a static backtest.



\---



\## 13. Key Lessons



The main lessons from the research process were:



\- simple strategies often outperform overly complex factor combinations

\- momentum strategies are regime-sensitive

\- concentration can improve returns but increase fragility

\- volatility filtering improved robustness

\- walk-forward testing is essential

\- live signal generation requires reliable automation

\- documenting rejected experiments improves credibility



\---



\## 14. Future Work



Future improvements include:



\- paper trading simulation

\- factor exposure regression

\- transaction cost stress testing

\- strategy comparison engine

\- alert system for new signals

\- database-backed signal storage

\- broker API integration

\- multi-strategy ensemble testing



\---



\## 15. Disclaimer



This project is for educational and research purposes only. It is not financial advice and should not be used as the sole basis for investment decisions.

