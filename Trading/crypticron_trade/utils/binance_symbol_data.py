from binance.client import Client
from django.conf import settings
from datetime import datetime, timedelta
import requests
# Binance API Keys from settings.py
API_KEY = settings.API_KEY
B_SECRET_KEY= settings.B_SECRET_KEY

# Initialize Binance Client
client = Client(API_KEY, B_SECRET_KEY)

# CoinMarketCap API Key
CMC_API_KEY = settings.COIN_MARKET_KEY

def format_large_number(value):
    """Convert large numbers into B (billion) or M (million) format."""
    if value >= 1_000_000_000:
        return f"${round(value / 1_000_000_000, 2)}B"
    elif value >= 1_000_000:
        return f"${round(value / 1_000_000, 2)}M"
    return f"${round(value, 2)}"


def calculate_percentage_change(old_price, new_price):
    """Calculate percentage change between two prices."""
    if old_price == 0:
        return "0%"
    change = ((new_price - old_price) / old_price) * 100
    return f"{'+' if change > 0 else ''}{round(change, 2)}%"


def get_market_cap_cmc(symbol):
    """Fetch market cap from CoinMarketCap using the symbol (e.g., BTC, ETH)."""
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
        params = {"symbol": symbol.replace("USDT", ""), "convert": "USD"}  # Remove USDT to match CMC format

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "data" in data and params["symbol"] in data["data"]:
            market_cap = data["data"][params["symbol"]]["quote"]["USD"]["market_cap"]
            # return format_large_number(market_cap)
            if market_cap is not None:  # Ensure it's not None before formatting
                return format_large_number(market_cap)
        return "N/A"

    except Exception as e:
        print(f"Error fetching market cap for {symbol}: {e}")
        return "N/A"


def get_binance_symbols_with_ohlc():
    """Fetch Binance trading pairs with price, 24h % change, 4h % change, volume, and market cap."""
    try:
        exchange_info = client.get_exchange_info()
        symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'].endswith("USDT")]

        crypto_data = []

        for symbol in symbols[:10]:  # Limit to top 10 to avoid rate limits
            try:
                # Get latest price and 24h change
                ticker = client.get_ticker(symbol=symbol)
                price = float(ticker['lastPrice'])
                change_24h = float(ticker['priceChangePercent'])
                volume_24h = float(ticker['quoteVolume'])

                # Fetch 4-hour old price
                four_hours_ago = int((datetime.utcnow() - timedelta(hours=4)).timestamp() * 1000)
                klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, startTime=four_hours_ago, limit=1)
                old_price_4h = float(klines[0][1]) if klines else price  # Use open price of 4 hours ago

                # Calculate 4-hour % change
                change_4h = calculate_percentage_change(old_price_4h, price)

                # Fetch Market Cap from CoinMarketCap
                market_cap = get_market_cap_cmc(symbol)

                # Crypto Name & Logo
                asset_name = symbol.replace("USDT", "")
                logo_url = f"https://cryptoicons.org/api/icon/{asset_name.lower()}/50"

                # Format Data
                crypto_data.append({
                    "symbol": symbol,
                    # "logo": logo_url,
                    "name": asset_name,
                    "price": f"${price:,.2f}",  # Format with commas
                    "24h_change": f"{'+' if change_24h > 0 else ''}{round(change_24h, 2)}%",
                    "4h_change": change_4h,
                    "24h_volume": format_large_number(volume_24h),
                    "market_cap": market_cap,  
                })

            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

        return crypto_data

    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return []


# def format_large_number(value):
#     """Convert large numbers into B (billion) or M (million) format."""
#     if value >= 1_000_000_000:
#         return f"${round(value / 1_000_000_000, 2)}B"
#     elif value >= 1_000_000:
#         return f"${round(value / 1_000_000, 2)}M"
#     return f"${round(value, 2)}"


# def calculate_percentage_change(old_price, new_price):
#     """Calculate percentage change between two prices."""
#     if old_price == 0:
#         return "0%"
#     change = ((new_price - old_price) / old_price) * 100
#     return f"{'+' if change > 0 else ''}{round(change, 2)}%"


# def get_binance_symbols_with_ohlc():
#     """Fetch Binance trading pairs with price, 24h % change, 4h % change, volume, and market cap."""
#     try:
#         exchange_info = client.get_exchange_info()
#         symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'].endswith("USDT")]

#         crypto_data = []

#         for symbol in symbols[:10]:  # Limit to top 10 to avoid rate limits
#             try:
#                 # Get latest price and 24h change
#                 ticker = client.get_ticker(symbol=symbol)
#                 price = float(ticker['lastPrice'])
#                 change_24h = float(ticker['priceChangePercent'])
#                 volume_24h = float(ticker['quoteVolume'])

#                 # Fetch 4-hour old price
#                 four_hours_ago = int((datetime.utcnow() - timedelta(hours=4)).timestamp() * 1000)
#                 klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, startTime=four_hours_ago, limit=1)
#                 old_price_4h = float(klines[0][1]) if klines else price  # Use open price of 4 hours ago

#                 # Calculate 4-hour % change
#                 change_4h = calculate_percentage_change(old_price_4h, price)

#                 # Market Cap (Placeholder, since Binance does not provide this)
#                 market_cap = "N/A"

#                 # Crypto Name & Logo
#                 asset_name = symbol.replace("USDT", "")
#                 logo_url = f"https://cryptoicons.org/api/icon/{asset_name.lower()}/50"

#                 # Format Data
#                 crypto_data.append({
#                     "symbol": symbol,
#                     "logo": logo_url,
#                     "name": asset_name,
#                     "price": f"${price:,.2f}",  # Format with commas
#                     "24h_change": f"{'+' if change_24h > 0 else ''}{round(change_24h, 2)}%",
#                     "4h_change": change_4h,
#                     "24h_volume": format_large_number(volume_24h),
#                     "market_cap": market_cap,  # Needs external API
#                 })

#             except Exception as e:
#                 print(f"Error fetching data for {symbol}: {e}")

#         return crypto_data

#     except Exception as e:
#         print(f"Error fetching Binance data: {e}")
#         return []
    
# Valid Binance Kline intervals
VALID_INTERVALS = {
    "1m": Client.KLINE_INTERVAL_1MINUTE,
    "5m": Client.KLINE_INTERVAL_5MINUTE,
    "15m": Client.KLINE_INTERVAL_15MINUTE,
    "30m": Client.KLINE_INTERVAL_30MINUTE,
    "1h": Client.KLINE_INTERVAL_1HOUR
}

def get_binance_symbols_with_interval(time_interval="1m"):
    """Fetch Binance symbols with their latest OHLC data for a given interval."""
    if time_interval not in VALID_INTERVALS:
        return {"error": "Invalid time interval. Choose from: 1m, 5m, 15m, 30m, 1h."}

    interval = VALID_INTERVALS[time_interval]

    try:
        exchange_info = client.get_exchange_info()
        symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'].endswith("USDT")]

        ohlc_data = {}
        for symbol in symbols[:10]:  # Limiting to first 10 symbols to prevent rate limits
            try:
                ticker = client.get_klines(symbol=symbol, interval=interval, limit=1)
                if ticker:
                    ohlc_data[symbol] = {
                        "Open": float(ticker[0][1]),
                        "High": float(ticker[0][2]),
                        "Low": float(ticker[0][3]),
                        "Close": float(ticker[0][4]),
                        "Time Interval": time_interval
                    }
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

        return ohlc_data
    except Exception as e:
        print(f"Error fetching Binance symbols: {e}")
        return {"error": "Failed to fetch Binance data."}
