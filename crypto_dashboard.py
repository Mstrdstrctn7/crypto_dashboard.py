@st.cache_data(ttl=300)
def get_prices():
    prices = {}
    for coin in COINS:
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

    return prices
