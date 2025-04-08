# import requests
# import numpy as np
# import pandas as pd
# from datetime import datetime, timedelta, timezone

# def fetch_live_candlestick_data(symbol):
#     """Fetch last 60 minutes of live candlestick data for a given symbol from Binance."""
#     binance_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=60"
#     response = requests.get(binance_url)
#     data = response.json()
    
#     # Extract relevant data
#     timestamps = [datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc) for entry in data]
#     open_prices = [float(entry[1]) for entry in data]
#     high_prices = [float(entry[2]) for entry in data]
#     low_prices = [float(entry[3]) for entry in data]
#     close_prices = [float(entry[4]) for entry in data]
    
#     return timestamps, open_prices, high_prices, low_prices, close_prices

# def predict_prices(last_price, last_time):
#     """Generate price predictions for the next 15 minutes."""
    
#     # Set the starting time for future predictions
#     start_time = (last_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
#     future_time = [start_time + timedelta(minutes=i) for i in range(15)]
    
#     # Generate random predicted prices (replace with an ML model later)
#     # predicted_prices = [last_price] + list(last_price + np.cumsum(np.random.uniform(-50, 50, size=14)))
#     predicted_prices = list(last_price + np.cumsum(np.random.uniform(-50, 50, size=15)))

#     # Generate confidence intervals
#     confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=15)
#     confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=15)
    
#     # Generate confidence percentage (mocked values for now)
#     confidence_percentage = np.random.uniform(80, 95, size=15)
    
#     # Structure prediction data
#     predictions = [
#         {
#             "timestamp_utc": t.isoformat(),
#             "predicted_price": round(p, 2),
#             "confidence_interval": f"{round(l, 2)} to {round(u, 2)}",
#             "confidence_percentage": f"{round(cp, 2)}%"
#         }
#         for t, p, l, u, cp in zip(future_time, predicted_prices, confidence_lower, confidence_upper, confidence_percentage)
#     ]
    
#     return predictions

# def get_latest_prediction(symbol="BTCUSDT"):
#     """Fetch the latest actual price, generate predictions, and return structured data."""
    
#     # Fetch live candlestick data
#     timestamps, open_prices, high_prices, low_prices, close_prices = fetch_live_candlestick_data(symbol)
    
#     # Get the latest actual data
#     last_time = timestamps[-1]
#     last_price = close_prices[-1]  # Latest live closing price
    
#     # Get runtime information
#     run_time_utc = datetime.now(timezone.utc).isoformat()  # Current execution time
#     actual_live_price = last_price  # Latest actual price at runtime
    
#     # Generate predictions
#     predictions = predict_prices(last_price, last_time)
    
#     # Combine results
#     response = {
#         "symbol": symbol,
#         "run_time_utc": run_time_utc,
#         "actual_live_price": actual_live_price,
#         "predictions": predictions
#     }
    
#     return response




#with historical data printing
# import requests
# import numpy as np
# from datetime import datetime, timedelta, timezone

# def fetch_historical_data(symbol):
#     """Fetch last 1-day historical candlestick data (1440 minutes) for a given symbol from Binance."""
#     binance_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=1440"
#     response = requests.get(binance_url)
#     data = response.json()
    
#     historical_data = [
#         {
#             "timestamp_utc": datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc).isoformat(),
#             "open": float(entry[1]),
#             "high": float(entry[2]),
#             "low": float(entry[3]),
#             "close": float(entry[4])
#         }
#         for entry in data
#     ]
    
#     return historical_data

# def predict_prices(last_price, last_time):
#     """Generate price predictions for the next 15 minutes."""
    
#     start_time = (last_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
#     future_time = [start_time + timedelta(minutes=i) for i in range(15)]
    
#     predicted_prices = list(last_price + np.cumsum(np.random.uniform(-50, 50, size=15)))
#     confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=15)
#     confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=15)
#     confidence_percentage = np.random.uniform(80, 95, size=15)
    
#     predictions = [
#         {
#             "timestamp_utc": t.isoformat(),
#             "predicted_price": round(p, 2),
#             "confidence_interval": f"{round(l, 2)} to {round(u, 2)}",
#             "confidence_percentage": f"{round(cp, 2)}%"
#         }
#         for t, p, l, u, cp in zip(future_time, predicted_prices, confidence_lower, confidence_upper, confidence_percentage)
#     ]
    
#     return predictions

# def get_latest_prediction(symbol="BTCUSDT"):
#     """Fetch historical price data (1 day), generate predictions, and return structured data."""
    
#     historical_data = fetch_historical_data(symbol)
    
#     last_data = historical_data[-1]
#     last_time = datetime.fromisoformat(last_data["timestamp_utc"])
#     last_price = last_data["close"]
    
#     run_time_utc = datetime.now(timezone.utc).isoformat()
    
#     predictions = predict_prices(last_price, last_time)
    
#     response = {
#         "symbol": symbol,
#         "run_time_utc": run_time_utc,
#         "actual_live_price": last_price,
#         "historical_data": historical_data,  # ✅ Includes last 1-day data (1440 candles)
#         "predictions": predictions
#     }
    
#     return response



# with SLTP
import requests
import numpy as np
from datetime import datetime, timedelta, timezone

# Binance API Base URL
BINANCE_API_BASE_URL = "https://api.binance.com/api/v3/klines"

def fetch_live_candlestick_data(symbol="BTCUSDT"):
    """
    Fetch the last 1440 candles of 1-minute interval OHLC data from Binance.
    """
    url = f"{BINANCE_API_BASE_URL}?symbol={symbol}&interval=1m&limit=1440"
    response = requests.get(url)
    data = response.json()
    
    historical_data = [
        {
            "timestamp_utc": datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc).isoformat(),
            "open": float(entry[1]),
            "high": float(entry[2]),
            "low": float(entry[3]),
            "close": float(entry[4])
        }
        for entry in data
    ]
    
    return historical_data

def predict_prices(last_price, last_time):
    """
    Generate future BTC price predictions at 1-minute intervals (next 15 periods).
    """
    start_time = (last_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
    future_time = [start_time + timedelta(minutes=1 * i) for i in range(15)]  # 1-minute intervals
    
    predicted_prices = list(last_price + np.cumsum(np.random.uniform(-50, 50, size=15)))
    confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=15)
    confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=15)
    confidence_percentage = np.random.uniform(80, 95, size=15)

    predictions = []
    for t, p, u, l, cp in zip(future_time, predicted_prices, confidence_upper, confidence_lower, confidence_percentage):
        diff = abs(p - last_price)
        tp1 = last_price + (diff * 0.5 if p > last_price else -diff * 0.5)
        tp2 = last_price + (diff * 1.0 if p > last_price else -diff * 1.0)
        sp = last_price - (diff * 0.5 if p > last_price else -diff * 0.5)

        predictions.append({
            "time": t.strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_price": round(p, 2),
            "tp1": round(tp1, 2),
            "tp2": round(tp2, 2),
            "sl": round(sp, 2),
            "confidence_interval": f"{l:.2f} to {u:.2f}",
            "confidence_percentage": f"{cp:.2f}%",
        })
    
    return predictions

def get_latest_prediction(symbol="BTCUSDT"):
    """
    Fetch live BTCUSDT data, generate predictions at 1-minute intervals, and return structured results.
    """
    historical_data = fetch_live_candlestick_data(symbol)
    last_data = historical_data[-1]
    last_time = datetime.fromisoformat(last_data["timestamp_utc"])
    last_price = last_data["close"]
    open_price = last_data["open"]
    high_price = last_data["high"]
    low_price = last_data["low"]
    close_price = last_data["close"]

    predictions = predict_prices(last_price, last_time)
    
    response_data = {
        "last_actual_price": round(last_price, 2),
        "last_time": last_time.strftime("%Y-%m-%d %H:%M:%S"),
        "historical_data": historical_data,
        "predictions": predictions
    }

    return response_data