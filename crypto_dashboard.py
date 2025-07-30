import streamlit as st
import requests
import pandas as pd

# Page setup
st.set_page_config(page_title="📱 Crypto Tracker", layout="wide")

# Constants
COINS = ["bitcoin", "ethereum", "solana"]
VS_CURRENCY = "usd"

# Sidebar for mobile settings
with st.sidebar:
    st.header("⚙️ Settings")
    selected_coins = st.multiselect("Select Coins", COINS, default=COINS)
    st.caption("Mobile-optimized view enabled ✔️")

# Price fetching from trusted exchanges
@st.cache_data(ttl=300)
def get_prices():
    prices = {}
    for coin in selected_coins:
        usd_prices = []

        # Binance
        try:
            symbol = coin.upper() + "USDT"
            r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
            binance_price = float(r.json()["price"])
            usd_prices.append(binance_price)
        except:
            pass

        # Coinbase
        try:
            symbol = coin.upper() + "-USD"
            r = requests.get(f"https://api.exchange.coinbase.com/products/{symbol}/ticker")
            coinbase_price = float(r.json()["price"])
            usd_prices.append(coinbase_price)
        except:
            pass

        # Kraken
        try:
            kraken_map = {"bitcoin": "XXBTZUSD", "ethereum": "XETHZUSD", "solana": "SOLUSD"}
            kr_symbol = kraken_map.get(coin)
            r = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={kr_symbol}")
            kraken_price = float(r.json()["result"][kr_symbol]["c"][0])
            usd_prices.append(kraken_price)
        except:
            pass

        if usd_prices:
            avg_price = sum(usd_prices) / len(usd_prices)
            prices[coin] = {VS_CURRENCY: avg_price}
        else:
            st.warning(f"⚠️ No price data found for {coin.title()}")

    return prices

# Load and show prices
st.title("📈 Real-Time Crypto Tracker")

prices = get_prices()

for coin in selected_coins:
    if coin in prices:
        price = prices[coin][VS_CURRENCY]
        with st.container():
            st.subheader(f"💰 {coin.title()}")
            st.markdown(f"<h2 style='color:lime;margin-top:-10px;'>${price:,.2f}</h2>", unsafe_allow_html=True)
            with st.expander("📊 Details"):
                st.markdown(f"- **Data Source:** Binance, Coinbase, Kraken")
                st.markdown(f"- **Average Price:** `${price:,.2f}`")
