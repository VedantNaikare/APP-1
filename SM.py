import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(
    page_title="Global Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# --------------------------
# Custom CSS
# --------------------------
st.markdown("""
<style>
.main{
    background-color:#0f172a;
}
div[data-testid="metric-container"]{
    background:#1e293b;
    padding:20px;
    border-radius:15px;
    border:1px solid #334155;
}
.stButton>button{
    width:100%;
    border-radius:10px;
    height:3em;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 Global Stock Market Dashboard")

st.write("Search any stock listed on Yahoo Finance and view live price with interactive historical charts.")

# --------------------------
# Popular Stocks
# --------------------------

popular = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Tesla": "TSLA",
    "Meta": "META",
    "NVIDIA": "NVDA",
    "Netflix": "NFLX",
    "Toyota": "7203.T",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS"
}

col1,col2=st.columns([2,1])

with col1:
    symbol=st.text_input(
        "Enter Yahoo Finance Stock Symbol",
        value="AAPL"
    )

with col2:
    suggestion=st.selectbox(
        "Popular Stocks",
        list(popular.keys())
    )

if st.button("Use Selected Suggestion"):
    symbol=popular[suggestion]

# --------------------------
# Time Period
# --------------------------

period=st.selectbox(
    "Select Time Period",
    ["1d","5d","1mo","3mo","6mo","1y","2y","5y","max"]
)

# --------------------------
# Download Data
# --------------------------

try:

    ticker=yf.Ticker(symbol)

    info=ticker.info

    hist=ticker.history(period=period)

    if hist.empty:
        st.error("No data available.")
        st.stop()

    current_price=info.get("currentPrice")

    previous_close=info.get("previousClose")

    change=current_price-previous_close

    percent=(change/previous_close)*100

    c1,c2,c3=st.columns(3)

    c1.metric(
        "Current Price",
        f"${current_price:,.2f}",
        f"{percent:.2f}%"
    )

    c2.metric(
        "Previous Close",
        f"${previous_close:,.2f}"
    )

    c3.metric(
        "Market Cap",
        f"{info.get('marketCap',0):,}"
    )

    st.subheader(info.get("longName",""))

    st.write(info.get("longBusinessSummary","No Description Available"))

    fig=go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            line=dict(width=3)
        )
    )

    fig.update_layout(
        title=f"{symbol} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark",
        height=600
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Historical Data")

    st.dataframe(hist)

except Exception as e:
    st.error(e)

st.sidebar.header("Popular Global Stocks")

for k,v in popular.items():
    st.sidebar.write(f"**{k}** : `{v}`")
