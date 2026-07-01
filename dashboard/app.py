import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from data.fetcher import get_stock_data, get_stock_info
from analysis.indicators import add_indicators, generate_signal
from ai.sentiment import get_news, analyze_with_ai

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Trading Assistant", layout="wide")
st.title("AI Trading Assistant")
st.caption("Live stock analysis powered by technical indicators + Gemini AI")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Search Stock")
    symbol = st.text_input("NSE Symbol", value="RELIANCE.NS",
                           help="Add .NS for NSE India (e.g. INFY.NS)")
    period = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y"], index=2)
    analyze_btn = st.button("Analyze", type="primary", use_container_width=True)

    st.divider()
    st.markdown("**Try these:**")
    st.code("RELIANCE.NS\nINFY.NS\nHDFCBANK.NS\nTATAMOTORS.NS\nWIPRO.NS")

# ── Main content ──────────────────────────────────────────────────────────────
if not analyze_btn:
    st.info("Enter a stock symbol in the sidebar and click Analyze.")
    st.stop()

with st.spinner(f"Fetching data for {symbol}..."):
    try:
        df = get_stock_data(symbol, period)
        info = get_stock_info(symbol)
    except Exception as e:
        st.error(f"Could not fetch data: {e}. Check the symbol (e.g. RELIANCE.NS)")
        st.stop()

df = add_indicators(df)
signal = generate_signal(df)

# ── Metric cards ──────────────────────────────────────────────────────────────
verdict_icon = {"BULLISH": "green", "BEARISH": "red", "NEUTRAL": "orange"}
col1, col2, col3, col4 = st.columns(4)
col1.metric("Company", info["name"])
col2.metric("Price", f"Rs. {signal['close']}")
col3.metric("Sector", info["sector"])
col4.metric("Signal", signal["verdict"])

st.divider()

# ── Charts + Signals ──────────────────────────────────────────────────────────
chart_col, signal_col = st.columns([2, 1])

with chart_col:
    st.subheader("Price Chart")

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 7),
        gridspec_kw={"height_ratios": [3, 1]},
        facecolor="#0e1117"
    )

    # Price + MAs + Bollinger
    ax1.set_facecolor("#0e1117")
    ax1.plot(df.index, df["Close"], label="Price", color="#4fc3f7", linewidth=2)
    ax1.plot(df.index, df["SMA_20"], label="SMA 20", color="orange", linewidth=1, linestyle="--")
    ax1.plot(df.index, df["SMA_50"], label="SMA 50", color="#ef5350", linewidth=1, linestyle="--")
    ax1.fill_between(df.index, df["BB_Upper"], df["BB_Lower"], alpha=0.08, color="gray", label="Bollinger Bands")
    ax1.set_ylabel("Price (Rs.)", color="white")
    ax1.tick_params(colors="white")
    ax1.legend(loc="upper left", facecolor="#1e2130", labelcolor="white", fontsize=8)
    ax1.grid(True, alpha=0.15)
    ax1.spines["bottom"].set_color("#333")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("#333")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))

    # RSI
    ax2.set_facecolor("#0e1117")
    rsi_colors = df["RSI"].apply(lambda x: "#ef5350" if x > 70 else ("#66bb6a" if x < 30 else "#4fc3f7"))
    ax2.bar(df.index, df["RSI"], color=rsi_colors, alpha=0.8, width=1)
    ax2.axhline(y=70, color="#ef5350", linestyle="--", alpha=0.6, linewidth=1)
    ax2.axhline(y=30, color="#66bb6a", linestyle="--", alpha=0.6, linewidth=1)
    ax2.set_ylabel("RSI", color="white")
    ax2.set_ylim(0, 100)
    ax2.tick_params(colors="white")
    ax2.grid(True, alpha=0.1)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["bottom"].set_color("#333")
    ax2.spines["left"].set_color("#333")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))

    plt.tight_layout(pad=1.5)
    st.pyplot(fig)
    plt.close()

with signal_col:
    st.subheader("Technical Signals")
    for s in signal["signals"]:
        st.write(f"- {s}")

    st.divider()
    st.subheader("RSI Reading")
    rsi = signal["rsi"]
    if rsi > 70:
        st.error(f"RSI {rsi} - Overbought")
    elif rsi < 30:
        st.success(f"RSI {rsi} - Oversold")
    else:
        st.info(f"RSI {rsi} - Neutral")

    st.divider()
    st.subheader("Key Levels")
    st.write(f"SMA 20: Rs. {signal['sma_20']}")
    st.write(f"SMA 50: Rs. {signal['sma_50']}")
    st.write(f"52W High: Rs. {info['52w_high']}")
    st.write(f"52W Low:  Rs. {info['52w_low']}")

# ── News + AI ─────────────────────────────────────────────────────────────────
st.divider()
news_col, ai_col = st.columns([1, 2])

with news_col:
    st.subheader("Recent News")
    company_name = info["name"]
    with st.spinner("Fetching news..."):
        headlines = get_news(company_name)
    for h in headlines:
        st.write(f"- {h}")

with ai_col:
    st.subheader("AI Research Summary")
    with st.spinner("Gemini is analyzing..."):
        summary = analyze_with_ai(symbol, company_name, signal, headlines)
    st.markdown(summary)
