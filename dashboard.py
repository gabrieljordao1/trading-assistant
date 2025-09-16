import streamlit as st
from trading_project import config, unusual_whales, reddit, fundamentals, strategy, autopilot

# Set up the dashboard
st.set_page_config(page_title="Trading Signals Assistant", layout="wide")
st.title("AI-Powered Trading Assistant")

# Sidebar for settings
st.sidebar.header("Settings")
symbols = st.sidebar.multiselect("Select symbols:", options=config.WATCHLIST, default=config.WATCHLIST)
run_autopilot = st.sidebar.checkbox("Enable Autopilot", value=config.is_autopilot_enabled())

if st.button("Run Analysis"):
    for symbol in symbols:
        st.subheader(f"Analysis for {symbol}")

        # Fetch options flow data
        flows = unusual_whales.get_recent_flow(symbol)
        st.write("Options Flow", flows if flows else "No data or API key missing")

        # Compute Reddit sentiment
        sentiment = reddit.get_sentiment_for_symbol(symbol)
        st.metric("Reddit Sentiment Score", f"{sentiment:.2f}")

        # Fetch fundamental data
        fund = fundamentals.get_fundamentals(symbol)
        if fund:
            st.write("Fundamentals", fund)
        else:
            st.warning("Could not retrieve fundamentals.")

        # Generate trading signal
        signal_result = strategy.generate_signal(symbol, flows, sentiment, fund)
        st.success(f"Signal: {signal_result['signal'].upper()}")
        st.caption(f"Reason: {signal_result['reason']}")

        # Optional autopilot trade execution
        if signal_result['signal'] in ['buy', 'sell']:
            if run_autopilot:
                autopilot.submit_order(symbol, signal_result['signal'], quantity=1)
                st.info(f"Executed {signal_result['signal']} 1 unit of {symbol}")
            else:
                st.info(f"[Dry-run] Would {signal_result['signal']} {symbol}")
        st.divider()
else:
    st.info("Click the 'Run Analysis' button to start.")
