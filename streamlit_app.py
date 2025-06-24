import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data.fetcher import fetch_stock_data
from src.models.var import (
    calculate_var_historical,
    calculate_var_parametric,
    calculate_var_monte_carlo,
)
from src.models.cvar import (
    calculate_cvar_historical,
    calculate_cvar_parametric,
    calculate_cvar_monte_carlo,
)

st.set_page_config(
    page_title="VaR and CVaR Risk Calculator", layout="wide", page_icon="⚠"
)

st.title("Value at Risk (VaR) and Conditional Value at Risk (CVaR) Calculator")

# Sidebar with Creator Title
st.sidebar.markdown("**Created by Utkarsh Sonpipre**")
st.sidebar.markdown("---")

st.sidebar.header("Portfolio Settings")

tickers = st.sidebar.text_input(
    "Enter NSE stock tickers (comma-separated)", "RELIANCE.NS,TCS.NS"
).split(",")
weights = st.sidebar.text_input(
    "Enter portfolio weights (comma-separated)", "0.5,0.5"
).split(",")
weights = [float(w) for w in weights]

if abs(sum(weights) - 1.0) > 1e-6:
    st.sidebar.error("Portfolio weights must sum to 1.0. Please adjust your inputs.")
    st.stop()

portfolio_value = st.sidebar.number_input(
    "Portfolio Value (₹)", min_value=1000, value=1000000, step=1000
)

st.sidebar.subheader("Risk Parameters")
confidence_level = st.sidebar.slider(
    "Confidence Level",
    min_value=0.9,
    max_value=0.99,
    value=0.95,
    step=0.01,
    help="Higher confidence levels result in higher VaR and CVaR values, indicating larger potential losses.",
)
time_horizon = st.sidebar.number_input(
    "Time Horizon (days)",
    min_value=1,
    value=1,
    step=1,
    help="Represents the number of days ahead for which potential losses are estimated. Longer horizons typically result in higher VaR and CVaR values.",
)

st.sidebar.subheader("Date Range")
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input(
    "Start Date",
    pd.to_datetime("2010-01-01"),
    help="The start date of historical data to use in calculations.",
)
end_date = col2.date_input(
    "End Date",
    min_value=start_date,
    max_value=pd.Timestamp("2025-06-22"),  # Latest historical date as of 01:38 AM IST, June 23, 2025
    value=pd.Timestamp("2025-06-22"),
    help="The end date of historical data to use in calculations.",
)

st.sidebar.subheader("Calculation Method")
calculation_method = st.sidebar.selectbox(
    "Select Method",
    ["Historical", "Parametric", "Monte Carlo"],
    help="Historical: Uses actual past returns  •  Parametric: Assumes returns follow a bell curve  •  🐐 Monte Carlo: Runs many random scenarios",
)
num_simulations = None
if calculation_method == "Monte Carlo":
    num_simulations = st.sidebar.number_input(
        "Number of Simulations",
        min_value=1000,
        value=10000,
        step=1000,
        help="More simulations generally provide more accurate results but take longer to compute.",
    )

st.sidebar.subheader("Additional Options")
use_rolling_window = st.sidebar.checkbox(
    "Use Rolling Window",
    help="Calculates VaR and CVaR using historical data over sliding time periods. Shows how risk estimates changed over time, displayed as a line graph instead of a histogram.",
)
if use_rolling_window:
    rolling_window = st.sidebar.slider(
        "Rolling Window Size",
        min_value=2,
        max_value=252,
        value=126,
        step=1,
        help="Number of past days used in each calculation point. Larger windows smooth out short-term fluctuations.",
    )


@st.cache_data
def get_stock_data(tickers, start_date, end_date):
    data = fetch_stock_data(tickers, start_date, end_date)
    returns = data.pct_change().dropna()
    return returns


returns = get_stock_data(tickers, start_date, end_date)

portfolio_returns = (returns * weights).sum(axis=1)


def calculate_var_cvar(
    returns, confidence_level, method, time_horizon, num_simulations=None
):
    simulated_returns = None
    if method == "Historical":
        var = calculate_var_historical(returns, confidence_level, time_horizon)
        cvar = calculate_cvar_historical(returns, confidence_level, time_horizon)
    elif method == "Parametric":
        var = calculate_var_parametric(returns, confidence_level, time_horizon)
        cvar = calculate_cvar_parametric(returns, confidence_level, time_horizon)
    elif method == "Monte Carlo":
        if num_simulations is None:
            raise ValueError(
                "Number of simulations must be provided for Monte Carlo method"
            )
        var, mc_returns = calculate_var_monte_carlo(
            returns, confidence_level, time_horizon, num_simulations
        )
        cvar, simulated_returns = calculate_cvar_monte_carlo(
            returns, confidence_level, time_horizon, num_simulations
        )
    else:
        raise ValueError("Invalid calculation method")
    return var, cvar, simulated_returns


if use_rolling_window:
    rolling_var = portfolio_returns.rolling(window=rolling_window).apply(
        lambda x: calculate_var_cvar(
            x, confidence_level, calculation_method, time_horizon, num_simulations
        )[0]
    )
    rolling_cvar = portfolio_returns.rolling(window=rolling_window).apply(
        lambda x: calculate_var_cvar(
            x, confidence_level, calculation_method, time_horizon, num_simulations
        )[1]
    )
    var, cvar = rolling_var.iloc[-1], rolling_cvar.iloc[-1]
else:
    var, cvar, simulated_returns = calculate_var_cvar(
        portfolio_returns,
        confidence_level,
        calculation_method,
        time_horizon,
        num_simulations,
    )

st.header("Risk Metrics")
col1, col2 = st.columns(2)

col1.metric(
    "Value at Risk (VaR)",
    f"₹{var * portfolio_value:.2f}",
    delta=None,
    help="VaR represents the maximum potential loss in the portfolio value over the specified time horizon, at the given confidence level. It answers the question: 'How much could I lose in a really bad case?'",
)
col2.metric(
    "Conditional Value at Risk (CVaR)",
    f"₹{cvar * portfolio_value:.2f}",
    delta=None,
    help="CVaR, also known as Expected Shortfall, represents the expected loss if the VaR is exceeded. It's the average of all losses greater than VaR, providing a more conservative risk estimate.",
)

st.header("Visualizations")

if use_rolling_window:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=rolling_var.index,
            y=rolling_var.values * portfolio_value,
            name="Rolling VaR",
            hovertemplate="Date: %{x|%Y-%m-%d}<br>VaR: ₹%{y:.2f} (%{text:.2%})<extra></extra>",
            text=rolling_var.values,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=rolling_cvar.index,
            y=rolling_cvar.values * portfolio_value,
            name="Rolling CVaR",
            hovertemplate="Date: %{x|%Y-%m-%d}<br>CVaR: ₹%{y:.2f} (%{text:.2%})<extra></extra>",
            text=rolling_cvar.values,
        )
    )
    fig.update_layout(
        title="Rolling VaR and CVaR",
        xaxis_title="Date",
        yaxis_title="Value (₹)",
        hovermode="x unified",
    )
    st.plotly_chart(fig)
else:
    fig = go.Figure()

    if calculation_method == "Monte Carlo":
        plot_returns = simulated_returns * portfolio_value
        plot_title = "Monte Carlo Simulated Returns Distribution with VaR and CVaR"
        subtitle = f"Based on {len(portfolio_returns)} historical data points, showing {num_simulations} simulations"
    else:
        plot_returns = portfolio_returns * portfolio_value
        if calculation_method == "Historical":
            plot_title = "Historical Returns Distribution with VaR and CVaR"
            subtitle = f"Using {len(portfolio_returns)} historical data points"
        else:
            plot_title = "Historical Returns Distribution with Parametric VaR and CVaR"
            subtitle = f"Using {len(portfolio_returns)} historical data points, assuming normal distribution"

    fig.add_trace(
        go.Histogram(
            x=plot_returns,
            nbinsx=100,
            name="Returns Distribution",
            marker=dict(line=dict(width=1, color="black")),
            hovertemplate="Return: ₹%{x:.2f}<br>Frequency: %{y}<extra></extra>",
        )
    )
    fig.add_vline(
        x=-var * portfolio_value,
        line_dash="dash",
        line_color="red",
        annotation_text=f"VaR: ₹{var * portfolio_value:.2f}",
    )
    fig.add_vline(
        x=-cvar * portfolio_value,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"CVaR: ₹{cvar * portfolio_value:.2f}",
    )
    fig.update_layout(
        title=f"{plot_title}<br><sup>{subtitle}</sup>",
        xaxis_title="Returns (₹)",
        yaxis_title="Frequency",
    )
    st.plotly_chart(fig)

st.write(f"Time Horizon: {time_horizon} days")
st.write(f"Confidence Level: {confidence_level:.2%}")
st.write(f"Calculation Method: {calculation_method}")
if calculation_method == "Monte Carlo":
    st.write(f"Number of Simulations: {num_simulations}")

st.markdown("---")
st.subheader("About VaR and CVaR")
st.write("""
- **Value at Risk (VaR)** represents the maximum potential loss in value of a portfolio over a defined period for a given confidence interval.
- **Conditional Value at Risk (CVaR)** represents the expected loss exceeding VaR. It provides a more conservative estimate of risk.
""")