from binance.client import Client
import os

# Binance API setup (Replace with your own API keys)
from django.conf import settings
#Binance key
API_KEY = settings.API_KEY
B_SECRET_KEY= settings.B_SECRET_KEY
client = Client(API_KEY, B_SECRET_KEY)

def fetch_sparkline_data(symbol="BTCUSDT", interval="1m", limit=60):
    """
    Fetch historical price data for a given symbol (default: last 60 minutes).
    """
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
        prices = [float(k[4]) for k in klines]  # 4th index = closing price
        return {"symbol": symbol, "prices": prices}
    except Exception as e:
        return {"error": str(e)}

# def fetch_multiple_sparklines(symbols=None, interval="1m", limit=60):
#     """
#     Fetch sparkline data for multiple symbols.
#     """
#     if symbols is None:
#         symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]

#     sparkline_data = {}

#     try:
#         for symbol in symbols:
#             result = fetch_sparkline_data(symbol, interval, limit)
#             if "error" not in result:
#                 sparkline_data[symbol] = result["prices"]

#         return {"data": sparkline_data}
#     except Exception as e:
#         return {"error": str(e)}
def fetch_multiple_sparklines(symbols=None, interval="1m", limit=60):
    """
    Fetch sparkline data for multiple symbols with the latest price.
    """
    if symbols is None:
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]

    sparkline_data = []

    try:
        for symbol in symbols:
            result = fetch_sparkline_data(symbol, interval, limit)
            
            if isinstance(result, dict) and "prices" in result and result["prices"]:
                latest_price = result["prices"][-1]  # Get latest price
                sparkline_data.append({
                    "symbol": symbol,
                    "price": latest_price,  # Add current price
                    "price_history": result["prices"]
                })

        return sparkline_data
    except Exception as e:
        return {"error": str(e)}
