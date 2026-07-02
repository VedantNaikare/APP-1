import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global Stock Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM UI/UX ---
st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background-color: #f8f9fa;
        }
        /* Custom metric card styling */
        .metric-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #1E3A8A;
            margin-bottom: 20px;
        }
        .metric-title {
            font-size: 0.9rem;
            color: #6B7280;
            text-transform: uppercase;
            font-weight: 600;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1F2937;
        }
        .metric-delta {
            font-size: 1rem;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("📈 Global Stock Market Analytics")
st.markdown("Fetch real-time data, explore trends, and visualize global stock performances beautifully.")
st.markdown("---")

# --- SIDEBAR & SUGGESTIONS ---
st.sidebar.header("🔍 Stock Selection")

# Curated stock suggestions with ticker mappings
suggestions = {
    "🇺🇸 US Tech Giants": {"Apple (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", "NVIDIA (NVDA)": "NVDA", "Tesla (TSLA)": "TSLA"},
    "🇮🇳 Indian Bluechips": {"Reliance Industries (RELIANCE.NS)": "RELIANCE.NS", "Tata Consultancy (TCS.NS)": "TCS.NS", "HDFC Bank (HDFCBANK.NS)": "HDFCBANK.NS"},
    "🇪🇺 European Leaders": {"ASML Holding (ASML)": "ASML", "LVMH (MC.PA)": "MC.PA", "SAP (SAP)": "SAP"},
    "🌏 Asian Markets": {"TSMC (TSM)": "TSM", "Sony Group (SONY)": "SONY", "Alibaba (BABA)": "BABA"}
}

st.sidebar.subheader("Quick Suggestions")
selected_ticker = ""

# Dropdown layout for quick suggestions
category = st.sidebar.selectbox("Choose a Market Category", list(suggestions.keys()))
suggestion_name = st.sidebar.selectbox("Select a Stock", list(suggestions[category].keys()))
suggested_ticker = suggestions[category][suggestion_name]

# Text Input for custom tickers (defaults to the selected suggestion)
ticker_input = st.sidebar.text_input(
    "Or Enter Any Global Ticker Symbol (e.g., GOOG, AMZN, INFY.NS)", 
    value=suggested_ticker
).strip().upper()

# Time period selector
st.sidebar.subheader("Timeframe Settings")
time_period = st.sidebar.selectbox(
    "Select Chart Time Period",
    options=["1D", "5D", "1M", "6M", "1Y", "5Y", "MAX"],
    index=4 # Defaults to 1Y
)

# Mapping periods to yfinance intervals
interval_mapping = {
    "1D": "5m", "5D": "15m", "1M": "1d", "6M": "1d", "1Y": "1d", "5Y": "1wk", "MAX": "1mo"
}

# --- DATA FETCHING ENGINE ---
@st.cache_data(ttl=300) # Cache data for 5 minutes to boost performance
def fetch_stock_data(ticker, period, interval):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period.lower(), interval=interval)
        info = stock.info
        return hist, info, None
    except Exception as e:
        return None, None, str(e)

if ticker_input:
    with st.spinner(f"Fetching data for {ticker_input}..."):
        hist, info, error = fetch_stock_data(ticker_input, time_period, interval_mapping[time_period])
    
    if error or hist.empty:
        st.error(f"❌ Could not retrieve data for **{ticker_input}**. Please verify the ticker symbol on Yahoo Finance.")
    else:
        # --- HERO METRICS DISPLAY ---
        company_name = info.get('longName', ticker_input)
        currency = info.get('currency', '$')
        
        # Calculate current price and changes
        if len(hist) >= 2:
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if time_period in ["1D", "5D"] else info.get('previousClose', hist['Close'].iloc[0])
            price_change = current_price - previous_close
            pct_change = (price_change / previous_close) * 100
        else:
            current_price = info.get('currentPrice', hist['Close'].iloc[-1] if not hist.empty else 0)
            price_change, pct_change = 0.0, 0.0

        delta_color = "#10B981" if price_change >= 0 else "#EF4444"
        delta_sign = "+" if price_change >= 0 else ""

        # UI Layout: Header & Real-time Metrics
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"{company_name} ({ticker_input})")
            st.caption(f"Sector: {info.get('sector', 'N/A')} | Industry: {info.get('industry', 'N/A')} | Currency: {currency}")
        
        with col2:
            # Custom styled metric card
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Current Price ({currency})</div>
                    <div class="metric-value">{current_price:,.2f}</div>
                    <div class="metric-delta" style="color: {delta_color};">
                        {delta_sign}{price_change:,.2f} ({delta_sign}{pct_change:.2f}%)
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # --- CHARTING SECTION ---
        st.markdown(### `Interactive Trend Analysis ({time_period})`)
        
        # Plotly Line Chart Configuration
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index, 
            y=hist['Close'], 
            mode='lines', 
            name='Close Price',
            line=dict(color='#1E3A8A' if price_change >= 0 else '#DC2626', width=2.5),
            hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> ' + currency + '%{y:,.2f}<extra></extra>'
        ))

        # Chart UI Tweaks
        fig.update_layout(
            template='plotly_white',
            margin=dict(l=20, r=20, t=20, b=20),
            height=450,
            xaxis=dict(
                showgrid=True,
                gridcolor='#E5E7EB',
                rangeslider=dict(visible=False)
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#E5E7EB',
                title=f"Price ({currency})"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- ADDITIONAL INFORMATION TABS ---
        tab1, tab2 = st.tabs(["📊 Key Fundamentals", "📝 Company Profile"])
        
        with tab1:
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            f_col1.metric("Day's High", f"{hist['High'].max():,.2f}" if not hist.empty else "N/A")
            f_col2.metric("Day's Low", f"{hist['Low'].min():,.2f}" if not hist.empty else "N/A")
            f_col3.metric("Market Cap", f"{info.get('marketCap', 0):,}" if info.get('marketCap') else "N/A")
            f_col4.metric("PE Ratio", f"{info.get('trailingPE', 'N/A')}")

        with tab2:
            st.markdown(f"**About {company_name}:**")
            st.write(info.get('longBusinessSummary', "No business summary available for this asset."))
else:
    st.info("💡 Select a stock suggestion from the sidebar or type a valid Yahoo Finance ticker to begin.")
