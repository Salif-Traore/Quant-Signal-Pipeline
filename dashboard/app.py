from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKTEST_PATH = PROJECT_ROOT / "data" / "backtests" / "portfolio_backtest_clean.parquet"
METRICS_PATH = PROJECT_ROOT / "data" / "backtests" / "performance_metrics.csv"
WALK_FORWARD_PATH = PROJECT_ROOT / "data" / "research" / "candidate_v2_walk_forward.csv"
TOP_N_SWEEP_PATH = PROJECT_ROOT / "data" / "research" / "top_n_parameter_sweep.csv"
LOOKBACK_SWEEP_PATH = PROJECT_ROOT / "data" / "research" / "lookback_sweep.csv"
VOL_SWEEP_PATH = PROJECT_ROOT / "data" / "research" / "volatility_filter_sweep.csv"
BREADTH_PATH = PROJECT_ROOT / "data" / "research" / "momentum_breadth.csv"


st.set_page_config(
    page_title="Quant Signal Pipeline Dashboard",
    layout="wide",
)


@st.cache_data
def load_backtest():
    df = pd.read_parquet(BACKTEST_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data
def load_csv(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def format_pct(value):
    return f"{value:.2%}"


def main():
    st.title("Quant Signal Pipeline Dashboard")

    st.caption(
        "Momentum strategy research dashboard: performance, walk-forward testing, parameter sweeps, and regime diagnostics."
    )

    backtest_df = load_backtest()
    metrics_df = load_csv(METRICS_PATH)
    walk_forward_df = load_csv(WALK_FORWARD_PATH)
    top_n_df = load_csv(TOP_N_SWEEP_PATH)
    lookback_df = load_csv(LOOKBACK_SWEEP_PATH)
    vol_sweep_df = load_csv(VOL_SWEEP_PATH)
    breadth_df = load_csv(BREADTH_PATH)

    latest_capital = backtest_df["capital"].iloc[-1]
    total_return = latest_capital / backtest_df["capital"].iloc[0] - 1

    returns = backtest_df["portfolio_return"].dropna()
    annualized_return = (1 + total_return) ** (252 / len(backtest_df)) - 1
    volatility = returns.std() * (252 ** 0.5)
    sharpe = returns.mean() / returns.std() * (252 ** 0.5)

    equity = backtest_df["capital"]
    drawdown = equity / equity.cummax() - 1
    max_drawdown = drawdown.min()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Final Capital", f"${latest_capital:,.0f}")
    col2.metric("Total Return", format_pct(total_return))
    col3.metric("Annualized Return", format_pct(annualized_return))
    col4.metric("Sharpe Ratio", f"{sharpe:.2f}")
    col5.metric("Max Drawdown", format_pct(max_drawdown))

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Performance",
            "Walk-Forward",
            "Parameter Sweeps",
            "Regime Analysis",
            "Raw Data",
        ]
    )

    with tab1:
        st.subheader("Equity Curve")

        fig = px.line(
            backtest_df,
            x="date",
            y="capital",
            title="Strategy Equity Curve",
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Drawdown")

        drawdown_df = backtest_df[["date"]].copy()
        drawdown_df["drawdown"] = drawdown

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
        ) * (252 ** 0.5)

        fig = px.line(
            rolling_df,
            x="date",
            y="rolling_sharpe_63d",
            title="63-Day Rolling Sharpe",
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Candidate V2 Walk-Forward Results")

        if not walk_forward_df.empty:
            st.dataframe(walk_forward_df, use_container_width=True)

            fig = px.bar(
                walk_forward_df,
                x="fold",
                y="sharpe_ratio",
                title="Walk-Forward Sharpe by Fold",
            )

            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(
                walk_forward_df,
                x="fold",
                y="max_drawdown",
                title="Walk-Forward Max Drawdown by Fold",
            )

            st.plotly_chart(fig, use_container_width=True)

            avg_cols = [
                "total_return",
                "annualized_return",
                "volatility",
                "sharpe_ratio",
                "max_drawdown",
            ]

            st.subheader("Average Walk-Forward Metrics")
            st.dataframe(
                walk_forward_df[avg_cols].mean().to_frame("average"),
                use_container_width=True,
            )
        else:
            st.warning("No walk-forward file found yet.")

    with tab3:
        st.subheader("Parameter Sweeps")

        if not top_n_df.empty:
            st.markdown("### Top-N Sweep")
            st.dataframe(top_n_df, use_container_width=True)

            fig = px.line(
                top_n_df,
                x="top_n",
                y="sharpe_ratio",
                markers=True,
                title="Top-N vs Sharpe",
            )

            st.plotly_chart(fig, use_container_width=True)

        if not lookback_df.empty:
            st.markdown("### Momentum Lookback Sweep")
            st.dataframe(lookback_df, use_container_width=True)

            fig = px.bar(
                lookback_df,
                x="momentum_col",
                y="sharpe_ratio",
                title="Momentum Lookback vs Sharpe",
            )

            st.plotly_chart(fig, use_container_width=True)

        if not vol_sweep_df.empty:
            st.markdown("### Volatility Filter Sweep")
            st.dataframe(vol_sweep_df, use_container_width=True)

            fig = px.line(
                vol_sweep_df,
                x="vol_quantile",
                y="sharpe_ratio",
                markers=True,
                title="Volatility Filter vs Sharpe",
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

            st.dataframe(breadth_df.tail(20), use_container_width=True)
        else:
            st.warning("No breadth file found yet.")

    with tab5:
        st.subheader("Backtest Data")
        st.dataframe(backtest_df, use_container_width=True)

        if not metrics_df.empty:
            st.subheader("Metrics CSV")
            st.dataframe(metrics_df, use_container_width=True)


if __name__ == "__main__":
    main()