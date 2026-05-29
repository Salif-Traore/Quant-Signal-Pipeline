from pathlib import Path
import sys

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from signals.momentum_signals import build_cross_sectional_momentum_signal
from portfolio.construction import build_monthly_rebalanced_portfolio


BACKTEST_PATH = PROJECT_ROOT / "data" / "backtests" / "portfolio_backtest_clean.parquet"
METRICS_PATH = PROJECT_ROOT / "data" / "backtests" / "performance_metrics.csv"
FEATURES_PATH = PROJECT_ROOT / "data" / "prepared" / "all_features.parquet"

WALK_FORWARD_PATH = PROJECT_ROOT / "data" / "research" / "candidate_v2_walk_forward.csv"
PAPER_LEDGER_PATH = PROJECT_ROOT / "data" / "live" / "paper_trading_ledger.csv"
WF_BACKTEST_PATH = PROJECT_ROOT / "data" / "backtests" / "walk_forward" / "walk_forward_backtests.parquet"

TOP_N_SWEEP_PATH = PROJECT_ROOT / "data" / "research" / "top_n_parameter_sweep.csv"
LOOKBACK_SWEEP_PATH = PROJECT_ROOT / "data" / "research" / "lookback_sweep.csv"
VOL_SWEEP_PATH = PROJECT_ROOT / "data" / "research" / "volatility_filter_sweep.csv"
BREADTH_PATH = PROJECT_ROOT / "data" / "research" / "momentum_breadth.csv"
REGIME_WF_PATH = PROJECT_ROOT / "data" / "research" / "candidate_v3_walk_forward.csv"
REGIME_BACKTEST_PATH = PROJECT_ROOT / "data" / "research" / "candidate_v3_backtests.parquet"
LIVE_SIGNALS_PATH = PROJECT_ROOT / "data" / "live" / "latest_signals.csv"


st.set_page_config(
    page_title="Quant Signal Pipeline Dashboard",
    layout="wide",
)


@st.cache_data
def load_backtest():
    df = pd.read_parquet(BACKTEST_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")


@st.cache_data
def load_features():
    df = pd.read_parquet(FEATURES_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["date", "ticker"])


@st.cache_data
def load_csv(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data
def load_parquet(path):
    if path.exists():
        df = pd.read_parquet(path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
    return pd.DataFrame()


def format_pct(x):
    return f"{x:.2%}"


def calculate_metrics(df):
    returns = df["portfolio_return"].dropna()

    total_return = df["capital"].iloc[-1] / df["capital"].iloc[0] - 1
    annualized_return = (1 + total_return) ** (252 / len(df)) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe = returns.mean() / returns.std() * np.sqrt(252)
    drawdown = df["capital"] / df["capital"].cummax() - 1
    max_drawdown = drawdown.min()

    return total_return, annualized_return, volatility, sharpe, max_drawdown


def build_benchmark_equity(features_df, ticker, initial_capital):
    benchmark = features_df[features_df["ticker"] == ticker].copy()
    benchmark = benchmark.sort_values("date")

    benchmark[ticker] = (
        initial_capital
        * (1 + benchmark["returns"].fillna(0)).cumprod()
    )

    return benchmark[["date", ticker]]


def build_current_holdings(features_df):
    signal_df = build_cross_sectional_momentum_signal(features_df)
    portfolio_df = build_monthly_rebalanced_portfolio(signal_df)

    latest_date = portfolio_df["date"].max()

    holdings = portfolio_df[
        (portfolio_df["date"] == latest_date)
        & (portfolio_df["weight"] > 0)
    ].copy()

    keep_cols = [
        "date",
        "ticker",
        "weight",
        "mom_1m",
        "vol_1m",
        "returns",
    ]

    existing_cols = [c for c in keep_cols if c in holdings.columns]

    return holdings[existing_cols].sort_values("weight", ascending=False)


def monte_carlo_simulation(returns, starting_capital, horizon_days, n_paths):
    returns = returns.dropna().values

    simulations = []

    for _ in range(n_paths):
        sampled_returns = np.random.choice(
            returns,
            size=horizon_days,
            replace=True,
        )

        capital_path = starting_capital * np.cumprod(1 + sampled_returns)

        simulations.append(capital_path)

    sim_df = pd.DataFrame(simulations).T
    sim_df.index = range(1, horizon_days + 1)

    return sim_df


def main():
    st.title("Quant Signal Pipeline Dashboard")

    st.caption(
        "Interactive research dashboard for momentum signals, benchmark comparison, walk-forward validation, parameter sweeps, holdings, live signals, and risk diagnostics."
    )

    backtest_df = load_backtest()
    features_df = load_features()

    metrics_df = load_csv(METRICS_PATH)
    walk_forward_df = load_csv(WALK_FORWARD_PATH)
    regime_wf_df = load_csv(REGIME_WF_PATH)
    regime_backtests_df = load_parquet(REGIME_BACKTEST_PATH)
    wf_backtests_df = load_parquet(WF_BACKTEST_PATH)

    top_n_df = load_csv(TOP_N_SWEEP_PATH)
    lookback_df = load_csv(LOOKBACK_SWEEP_PATH)
    vol_sweep_df = load_csv(VOL_SWEEP_PATH)
    breadth_df = load_csv(BREADTH_PATH)
    live_signals_df = load_csv(LIVE_SIGNALS_PATH)
    paper_ledger_df = load_csv(PAPER_LEDGER_PATH)

    min_date = backtest_df["date"].min().date()
    max_date = backtest_df["date"].max().date()

    st.sidebar.header("Dashboard Controls")

    selected_date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    selected_benchmarks = st.sidebar.multiselect(
        "Benchmarks",
        options=["SPY", "QQQ"],
        default=["SPY", "QQQ"],
    )

    selected_metric = st.sidebar.selectbox(
        "Primary Metric",
        options=[
            "sharpe_ratio",
            "total_return",
            "annualized_return",
            "volatility",
            "max_drawdown",
        ],
        index=0,
    )
    selected_strategy_view = st.sidebar.selectbox(
         "Strategy View",
         options=[
         "Production Cross-Sectional",
         "Regime Scaling Candidate",
        ],
    )

    monte_carlo_paths = st.sidebar.slider(
        "Monte Carlo Paths",
        min_value=100,
        max_value=2000,
        value=500,
        step=100,
    )
    starting_capital_override = st.sidebar.slider(
        "Starting Capital",
        min_value=10_000,
        max_value=1_000_000,
        value=100_000,
        step=10_000,
    )
    monte_carlo_horizon = st.sidebar.slider(
        "Monte Carlo Horizon Days",
        min_value=21,
        max_value=252,
        value=126,
        step=21,
    )

    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date = pd.to_datetime(selected_date_range[0])
        end_date = pd.to_datetime(selected_date_range[1])

        backtest_df = backtest_df[
            (backtest_df["date"] >= start_date)
            & (backtest_df["date"] <= end_date)
        ].copy()

    original_initial_capital = backtest_df["capital"].iloc[0]

    scale_factor = (
    starting_capital_override
    / original_initial_capital
    )

    backtest_df["capital"] = (
    backtest_df["capital"]
    * scale_factor
    )

    initial_capital = starting_capital_override
    latest_capital = backtest_df["capital"].iloc[-1]

    total_return, annualized_return, volatility, sharpe, max_drawdown = (
        calculate_metrics(backtest_df)
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Final Capital", f"${latest_capital:,.0f}")
    col2.metric("Total Return", format_pct(total_return))
    col3.metric("Annualized Return", format_pct(annualized_return))
    col4.metric("Sharpe Ratio", f"{sharpe:.2f}")
    col5.metric("Max Drawdown", format_pct(max_drawdown))

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
        [
            "Performance",
            "Walk-Forward",
            "Parameter Sweeps",
            "Regime Analysis",
            "Holdings",
            "Live Signals",
            "Paper Trading",
            "Monte Carlo",
            "Downloads",
        ]
    )

    with tab1:
        st.subheader("Strategy vs Benchmarks")

        comparison_df = backtest_df[["date", "capital"]].copy()
        comparison_df = comparison_df.rename(columns={"capital": "Strategy"})

        for ticker in selected_benchmarks:
            bench = build_benchmark_equity(
                features_df,
                ticker,
                initial_capital,
            )

            comparison_df = comparison_df.merge(
                bench,
                on="date",
                how="left",
            )

        plot_cols = ["Strategy"] + selected_benchmarks

        fig = px.line(
            comparison_df,
            x="date",
            y=plot_cols,
            title="Strategy vs Benchmarks",
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Drawdown")

        drawdown_df = backtest_df[["date"]].copy()
        drawdown_df["drawdown"] = (
            backtest_df["capital"]
            / backtest_df["capital"].cummax()
            - 1
        )

        fig = px.line(
            drawdown_df,
            x="date",
            y="drawdown",
            title="Strategy Drawdown",
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Rolling Sharpe")

        rolling_df = backtest_df[["date", "portfolio_return"]].copy()

        rolling_df["rolling_sharpe_63d"] = (
            rolling_df["portfolio_return"].rolling(63).mean()
            / rolling_df["portfolio_return"].rolling(63).std()
        ) * np.sqrt(252)

        fig = px.line(
            rolling_df,
            x="date",
            y="rolling_sharpe_63d",
            title="63-Day Rolling Sharpe",
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Rolling Alpha / Beta vs SPY")

        spy_returns = features_df[
            features_df["ticker"] == "SPY"
        ][["date", "returns"]].rename(columns={"returns": "spy_return"})

        alpha_beta_df = backtest_df[["date", "portfolio_return"]].merge(
            spy_returns,
            on="date",
            how="left",
        )

        rolling_cov = (
            alpha_beta_df["portfolio_return"]
            .rolling(63)
            .cov(alpha_beta_df["spy_return"])
        )

        rolling_var = alpha_beta_df["spy_return"].rolling(63).var()

        alpha_beta_df["rolling_beta_63d"] = rolling_cov / rolling_var

        alpha_beta_df["rolling_alpha_63d"] = (
            alpha_beta_df["portfolio_return"].rolling(63).mean()
            - alpha_beta_df["rolling_beta_63d"]
            * alpha_beta_df["spy_return"].rolling(63).mean()
        ) * 252

        fig = px.line(
            alpha_beta_df,
            x="date",
            y=["rolling_alpha_63d", "rolling_beta_63d"],
            title="63-Day Rolling Alpha and Beta vs SPY",
        )

        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        st.subheader("Walk-Forward Results")

        if selected_strategy_view == "Production Cross-Sectional":
            display_wf_df = walk_forward_df
            display_backtests_df = wf_backtests_df
        else:
            display_wf_df = regime_wf_df
            display_backtests_df = regime_backtests_df

        st.caption(f"Viewing: {selected_strategy_view}")

        if not display_wf_df.empty:
            st.dataframe(display_wf_df, use_container_width=True)

            if "fold" in display_wf_df.columns:
                selected_fold = st.selectbox(
                    "Select Fold",
                    options=display_wf_df["fold"].unique(),
                )

                fold_row = display_wf_df[
                    display_wf_df["fold"] == selected_fold
                ]

                st.write(fold_row)

            fig = px.bar(
                display_wf_df,
                x="fold",
                y=selected_metric,
                title=f"{selected_strategy_view}: Walk-Forward {selected_metric} by Fold",
            )

            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(
                display_wf_df,
                x="fold",
                y="max_drawdown",
                title=f"{selected_strategy_view}: Walk-Forward Max Drawdown by Fold",
            )

            st.plotly_chart(fig, use_container_width=True)

            avg_cols = [
                "total_return",
                "annualized_return",
                "volatility",
                "sharpe_ratio",
                "max_drawdown",
            ]

            available_avg_cols = [
                col for col in avg_cols
                if col in display_wf_df.columns
            ]

            st.subheader("Average Walk-Forward Metrics")

            st.dataframe(
                display_wf_df[available_avg_cols].mean().to_frame("average"),
                use_container_width=True,
            )
        else:
            st.warning(
                f"No walk-forward metrics found for {selected_strategy_view}."
            )

        st.subheader("Fold-by-Fold Equity Curves")

        if (
            not display_backtests_df.empty
            and "fold" in display_backtests_df.columns
        ):
            selected_folds = st.multiselect(
                "Select folds to plot",
                options=sorted(display_backtests_df["fold"].unique()),
                default=sorted(display_backtests_df["fold"].unique()),
            )

            fold_plot_df = display_backtests_df[
                display_backtests_df["fold"].isin(selected_folds)
            ].copy()

            fig = px.line(
                fold_plot_df,
                x="date",
                y="capital",
                color="fold",
                title=f"{selected_strategy_view}: Walk-Forward Equity Curves",
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                f"No fold equity parquet found for {selected_strategy_view}."
            )

    with tab3:
        st.subheader("Parameter Sweeps")

        if not top_n_df.empty:
            st.markdown("### Top-N Sweep")
            st.dataframe(top_n_df, use_container_width=True)

            fig = px.line(
                top_n_df,
                x="top_n",
                y=selected_metric,
                markers=True,
                title=f"Top-N vs {selected_metric}",
            )

            st.plotly_chart(fig, use_container_width=True)

        if not lookback_df.empty:
            st.markdown("### Momentum Lookback Sweep")
            st.dataframe(lookback_df, use_container_width=True)

            fig = px.bar(
                lookback_df,
                x="momentum_col",
                y=selected_metric,
                title=f"Momentum Lookback vs {selected_metric}",
            )

            st.plotly_chart(fig, use_container_width=True)

        if not vol_sweep_df.empty:
            st.markdown("### Volatility Filter Sweep")
            st.dataframe(vol_sweep_df, use_container_width=True)

            fig = px.line(
                vol_sweep_df,
                x="vol_quantile",
                y=selected_metric,
                markers=True,
                title=f"Volatility Filter vs {selected_metric}",
            )

            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Momentum Breadth")

        if not breadth_df.empty:
            breadth_df["date"] = pd.to_datetime(breadth_df["date"])

            fig = px.line(
                breadth_df,
                x="date",
                y=["momentum_breadth", "breadth_30d_ma"],
                title="Momentum Breadth Through Time",
            )

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(breadth_df.tail(30), use_container_width=True)
        else:
            st.warning("No breadth file found.")

    with tab5:
        st.subheader("Current Holdings Panel")

        holdings_df = build_current_holdings(features_df)

        if not holdings_df.empty:
            st.dataframe(holdings_df, use_container_width=True)

            fig = px.bar(
                holdings_df,
                x="ticker",
                y="weight",
                title="Current Portfolio Weights",
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No current holdings found.")

    with tab6:
        st.subheader("Latest Live Signals")

        if not live_signals_df.empty:
            live_signals_df["date"] = pd.to_datetime(live_signals_df["date"])

            latest_signal_date = live_signals_df["date"].max()

            st.caption(f"Signal Date: {latest_signal_date.date()}")

            st.dataframe(
                live_signals_df,
                use_container_width=True,
            )

            fig = px.bar(
                live_signals_df,
                x="ticker",
                y="weight",
                title="Latest Portfolio Weights",
            )

            st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "Download Latest Signals CSV",
                live_signals_df.to_csv(index=False),
                file_name="latest_signals.csv",
                mime="text/csv",
                key="live_signals_tab_download",
            )

        else:
            st.warning(
                "No live signal file found. Run scripts/generate_live_signals.py first."
            )

    with tab7:
        st.subheader("Paper Trading Ledger")

        if not paper_ledger_df.empty:
            paper_ledger_df["date"] = pd.to_datetime(paper_ledger_df["date"])

            latest_paper_date = paper_ledger_df["date"].max()
            latest_rows = paper_ledger_df[
                paper_ledger_df["date"] == latest_paper_date
            ].copy()

            latest_capital = latest_rows["paper_capital"].iloc[0]

            col1, col2, col3 = st.columns(3)

            col1.metric("Latest Paper Date", str(latest_paper_date.date()))
            col2.metric("Paper Capital", f"${latest_capital:,.0f}")
            col3.metric("Active Positions", len(latest_rows))

            st.subheader("Latest Paper Positions")
            st.dataframe(latest_rows, use_container_width=True)

            fig = px.bar(
                latest_rows,
                x="ticker",
                y="dollar_allocation",
                title="Latest Paper Dollar Allocation",
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Full Paper Trading Ledger")
            st.dataframe(paper_ledger_df, use_container_width=True)

            st.download_button(
                "Download Paper Trading Ledger CSV",
                paper_ledger_df.to_csv(index=False),
                file_name="paper_trading_ledger.csv",
                mime="text/csv",
                key="download_paper_trading_ledger",
            )
        else:
            st.warning(
                "No paper trading ledger found. Run scripts/update_paper_trading_ledger.py first."
            )

    with tab8:
        st.subheader("Monte Carlo Simulation")

        st.write(
            "Simulation resamples historical strategy daily returns to estimate possible future capital paths."
        )

        sim_df = monte_carlo_simulation(
            returns=backtest_df["portfolio_return"],
            starting_capital=latest_capital,
            horizon_days=monte_carlo_horizon,
            n_paths=monte_carlo_paths,
        )

        percentiles = pd.DataFrame(
            {
                "p05": sim_df.quantile(0.05, axis=1),
                "p50": sim_df.quantile(0.50, axis=1),
                "p95": sim_df.quantile(0.95, axis=1),
            }
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=percentiles.index,
                y=percentiles["p95"],
                name="95th Percentile",
                mode="lines",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=percentiles.index,
                y=percentiles["p50"],
                name="Median",
                mode="lines",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=percentiles.index,
                y=percentiles["p05"],
                name="5th Percentile",
                mode="lines",
            )
        )

        fig.update_layout(
            title="Monte Carlo Projected Capital Range",
            xaxis_title="Future Trading Days",
            yaxis_title="Capital",
        )

        st.plotly_chart(fig, use_container_width=True)

        final_values = sim_df.iloc[-1]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "5th Percentile Final",
            f"${final_values.quantile(0.05):,.0f}",
        )
        col2.metric(
            "Median Final",
            f"${final_values.quantile(0.50):,.0f}",
        )
        col3.metric(
            "95th Percentile Final",
            f"${final_values.quantile(0.95):,.0f}",
        )

    with tab9:
        st.subheader("Downloadable CSVs")

        st.download_button(
            "Download Backtest CSV",
            backtest_df.to_csv(index=False),
            file_name="backtest_results.csv",
            mime="text/csv",
        )

        if not live_signals_df.empty:
            st.download_button(
                "Download Latest Signals CSV",
                live_signals_df.to_csv(index=False),
                file_name="latest_signals.csv",
                mime="text/csv",
                key="downloads_tab_live_signals",
            )

        if not walk_forward_df.empty:
            st.download_button(
                "Download Walk-Forward CSV",
                walk_forward_df.to_csv(index=False),
                file_name="walk_forward_results.csv",
                mime="text/csv",
            )

        if not top_n_df.empty:
            st.download_button(
                "Download Top-N Sweep CSV",
                top_n_df.to_csv(index=False),
                file_name="top_n_sweep.csv",
                mime="text/csv",
            )

        if not lookback_df.empty:
            st.download_button(
                "Download Lookback Sweep CSV",
                lookback_df.to_csv(index=False),
                file_name="lookback_sweep.csv",
                mime="text/csv",
            )

        if not vol_sweep_df.empty:
            st.download_button(
                "Download Volatility Sweep CSV",
                vol_sweep_df.to_csv(index=False),
                file_name="volatility_filter_sweep.csv",
                mime="text/csv",
            )

        if not breadth_df.empty:
            st.download_button(
                "Download Momentum Breadth CSV",
                breadth_df.to_csv(index=False),
                file_name="momentum_breadth.csv",
                mime="text/csv",
            )

        if not metrics_df.empty:
            st.subheader("Metrics CSV")
            st.dataframe(metrics_df, use_container_width=True)

        st.subheader("Raw Backtest Data")
        st.dataframe(backtest_df, use_container_width=True)


if __name__ == "__main__":
    main()