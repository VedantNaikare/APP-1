import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- Page Configuration & Styling ---
st.set_page_config(
    page_title="Global Stock Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI/UX card styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4a90e2;
        margin-bottom: 10px;
    }
    .stButton>button {
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Title and Header ---
st.title("📈 Global Market Analytics Dashboard")
st.caption("Real-time global market data retrieval powered by Yahoo Finance")
st.markdown("---")

# --- Quick suggestions dictionary ---
SUGGESTIONS = {
    "Apple (USA)": "AAPL",
    "NVIDIA (USA)": "NVDA",
    "Reliance Industries (India)": "RELIANCE.NS",
    "ASML Holding (Europe)": "ASML",
    "Toyota Motor (Japan)": "7203.T",
    "Sony Group (Japan)": "6758.T"
}

# --- Sidebar Controls ---
st.sidebar.header("🔍 Market Explorer")

# Initialize session state for ticker input if it doesn't exist
if "ticker_input" not in st.session_state:
    st.session_state["ticker_input"] = "AAPL"

# Add shortcut suggestion buttons in sidebar
st.sidebar.markdown("### Quick Recommendations")
for label, sym in SUGGESTIONS.items():
    if st.sidebar.button(f"🏢 {label} ({sym})", use_container_width=True):
        st.session_state["ticker_input"] = sym
        # Force a rerun to instantly update the text field value
        st.rerun()

# Main Text Input for Ticker Search
ticker_symbol = st.sidebar.text_input(
    "Enter Global Ticker Symbol Manually", 
    value=st.session_state["ticker_input"]
).upper().strip()

# Period configuration mappings
time_frames = {
    "1 Day": {"period": "1d", "interval": "5m"},
    "1 Week": {"period": "5d", "interval": "15m"},
    "1 Month": {"period": "1mo", "interval": "1d"},
    "6 Months": {"period": "6mo", "interval": "1d"},
    "Year to Date": {"period": "ytd", "interval": "1d"},
    "1 Year": {"period": "1y", "interval": "1d"},
    "5 Years": {"period": "5y", "interval": "1wk"}
}

selected_tf = st.sidebar.selectbox("Select Time Horizon", list(time_frames.keys()), index=2)

# --- Data Fetching Logic (Cached for Performance) ---
@st.cache_data(ttl=60)  # Cache data for 1 minute
def load_stock_data(ticker, period, interval):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        info = stock.info
        return hist, info, None
    except Exception as e:
        return None, None, str(e)

if ticker_symbol:
    with st.spinner(f"Fetching real-time data for {ticker_symbol}..."):
        period_param = time_frames[selected_tf]["period"]
        interval_param = time_frames[selected_tf]["interval"]
        
        hist_data, stock_info, error = load_stock_data(ticker_symbol, period_param, interval_param)

    if error or hist_data is None or hist_data.empty:
        st.error(f"❌ Could not retrieve data for ticker **'{ticker_symbol}'**. Please check the spelling or market availability.")
        st.info("💡 Note: For international stocks, remember to add their market suffix (e.g., `.NS` for India, `.T` for Tokyo).")
    else:
        # --- UI Extraction and Calculations ---
        company_name = stock_info.get('longName', ticker_symbol)
        currency = stock_info.get('currency', '$')
        
        # Get price deltas safely
        current_price = hist_data['Close'].iloc[-1]
        previous_close = stock_info.get('previousClose', hist_data['Close'].iloc[0])
        price_change = current_price - previous_close
        price_change_pct = (price_change / previous_close) * 100

        # --- Main Layout View ---
        col_header, col_meta = st.columns([3, 1])
        with col_header:
            st.subheader(f"{company_name} ({ticker_symbol})")
            st.caption(f"Sector: {stock_info.get('sector', 'N/A')} | Industry: {stock_info.get('industry', 'N/A')}")
        
        # Metric Cards Rows
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric(
            label="Current Spot Price", 
            value=f"{current_price:,.2f} {currency}", 
            delta=f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
        )
        m_col2.metric(label="Period High", value=f"{hist_data['High'].max():,.2f} {currency}")
        m_col3.metric(label="Period Low", value=f"{hist_data['Low'].min():,.2f} {currency}")
        
        # Format Market Cap cleanly
        m_cap = stock_info.get('marketCap')
        m_cap_str = f"{m_cap:,} {currency}" if m_cap else "N/A"
        m_col4.metric(label="Market Cap", value=m_cap_str)

        # --- Charts Area ---
        st.markdown(f"### Interactive Price Chart — `{selected_tf}` View")
        
        # Preparing chart data frame
        chart_df = hist_data[['Close']].copy()
        
        # Clean index representation for cleaner visualization x-axis
        if period_param in ['1d', '5d']:
            chart_df.index = chart_df.index.strftime('%Y-%m-%d %H:%M')
        else:
            chart_df.index = chart_df.index.strftime('%Y-%m-%d')
            
        st.line_chart(chart_df, color="#29b5e8", use_container_width=True)

        # --- Descriptive Profiles / Business Summary ---
        with st.expander("📖 View Company Deep Dive & Business Summary"):
            st.markdown(f"**About {company_name}:**")
            st.write(stock_info.get('longBusinessSummary', "No descriptive summary available for this specific asset listing."))
else:
    st.info("← Select a recommended stock or enter a valid ticker symbol in the sidebar menu to view analytics.")
