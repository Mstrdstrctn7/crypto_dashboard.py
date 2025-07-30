import streamlit as st
import hashlib
import requests
import pandas as pd
import numpy as np
from textblob import TextBlob
from datetime import datetime, timedelta

# ----------- LOGIN PROTECTION ------------
def check_credentials():
    def hash_string(s):
        return hashlib.sha256(s.encode()).hexdigest()

    # Store hashed username and password
    correct_username_hash = hash_string("t-daddy")
    correct_password_hash = hash_string("Elisamylov5424")

    if "auth_ok" not in st.session_state:
        st.session_state["auth_ok"] = False

    if not st.session_state["auth_ok"]:
        with st.form("login_form"):
            st.title("🔒 Secure Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if (
                    hash_string(username) == correct_username_hash and
                    hash_string(password) == correct_password_hash
                ):
                    st.session_state["auth_ok"] = True
                    st.success("✅ Access granted")
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password")
    return st.session_state["auth_ok"]

if not check_credentials():
    st.stop()

# ---------- APP STARTS HERE ----------
st.set_page_config(page_title="Crypto Analyzer", layout="wide")

COINS = ["bitcoin", "ethereum", "solana"]
VS_CURRENCY = "usd"
PRICE_API = f"https://api.coingecko.com/api/v3/simple/price"
CHART_API = "https://api.coingecko.com/api/v3/coins/{{}}/market_chart"
SENTIMENT_SOURCES = {
    "Bitcoin": "Bitcoin is trending with strong momentum and community backing.",
    "Ethereum": "Ethereum is receiving mixed sentiment around gas fees and ETH 2.0.",
    "Solana": "Solana is gaining buzz in DeFi and NFTs but has mixed reliability reviews."
}

@st.cache_data(ttl=300)
def get_prices():
    params = {
        "ids": ",".join(COINS),
        "vs_currencies": VS_CURRENCY
    }
    r = requests.get(PRICE_API, params=params)
    return r.json()

@st.cache_data(ttl=900)
def get_price_history(coin):
    params = {"vs_currency": VS_CURRENCY, "days": "7", "interval": "hourly"}
    r = requests.get(CHART_API.format(coin), params=params)
    data = r.json()
    prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
    return prices

def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

def calculate_momentum(prices):
    returns = prices["price"].pct_change()
    momentum = returns.rolling(window=3).mean().iloc[-1]
    volatility = returns.rolling(window=3).std().iloc[-1]
    return momentum, volatility

# ---------- DASHBOARD ----------
st.title("📊 Crypto Analyzer — Real-Time Insights")
st.markdown("Get price trends, sentiment, momentum & risk for key coins.")

price_data = get_prices()
cols = st.columns(len(COINS))

results = []

for i, coin in enumerate(COINS):
    name = coin.capitalize()
    prices = get_price_history(coin)
    current_price = price_data[coin][VS_CURRENCY]

    momentum, volatility = calculate_momentum(prices)
    sentiment_score = analyze_sentiment(SENTIMENT_SOURCES.get(name, ""))

    sharpe = (momentum / volatility) if volatility else 0

    with cols[i]:
        st.subheader(f"{name} — ${current_price:,.2f}")
        st.line_chart(prices.set_index("timestamp")["price"], height=200)

        st.metric("📈 Momentum", f"{momentum:.4f}")
        st.metric("📊 Volatility", f"{volatility:.4f}")
        st.metric("🧠 Sentiment", f"{sentiment_score:.2f}")
        st.metric("💰 Sharpe Ratio", f"{sharpe:.2f}")

        results.append({
            "coin": name,
            "price": current_price,
            "momentum": momentum,
            "volatility": volatility,
            "sentiment": sentiment_score,
            "sharpe": sharpe
        })

df = pd.DataFrame(results)
best = df.sort_values("sharpe", ascending=False).iloc[0]

st.divider()
st.success(
    f"📢 Best move right now: **{best['coin']}** at ${best['price']:,.2f} "
    f"(Sharpe Ratio: {best['sharpe']:.2f})"
)
