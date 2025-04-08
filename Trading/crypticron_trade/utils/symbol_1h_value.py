# import requests
# import numpy as np
# from datetime import datetime, timedelta, timezone

# # Binance API Base URL
# BINANCE_API_BASE_URL = "https://api.binance.com/api/v3/klines"

# def fetch_hourly_candlestick_data(symbol="BTCUSDT"):
#     """Fetch the last 24 hours of candlestick data for a given symbol from Binance."""
#     url = f"{BINANCE_API_BASE_URL}?symbol={symbol}&interval=1h&limit=24"
#     response = requests.get(url)
#     data = response.json()
    
#     timestamps = [datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc) for entry in data]
#     close_prices = [float(entry[4]) for entry in data]
    
#     return timestamps, close_prices

# def predict_prices(last_price, last_time):
#     """Predict prices for the next 1 hour in 15-minute intervals."""
    
#     # Generate future timestamps
#     future_time = [last_time + timedelta(minutes=i) for i in range(0, 76, 15)]  # 0 to 75 min
    
#     # Generate random predictions (replace with ML model later)
#     predicted_prices = list(last_price + np.cumsum(np.random.uniform(-50, 50, size=6)))

#     # Generate confidence intervals
#     confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=6)
#     confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=6)
#     confidence_intervals = [(round(l, 2), round(u, 2)) for l, u in zip(confidence_lower, confidence_upper)]
    
#     return future_time, predicted_prices, confidence_intervals

# def get_crypto_prediction_data(symbol="BTCUSDT"):
#     """Fetch cryptocurrency data, predict future prices, and return structured data."""
    
#     # Fetch live data for the given symbol
#     timestamps, close_prices = fetch_hourly_candlestick_data(symbol)
    
#     # Get last actual price and time
#     last_time = timestamps[-1]
#     last_price = close_prices[-1]
    
#     # Get current UTC time
#     run_time_utc = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

#     # Predict future prices
#     future_time, predicted_prices, confidence_intervals = predict_prices(last_price, last_time)

#     # Generate confidence percentage (mock data for now)
#     confidence_percentage = np.random.uniform(80, 95, size=len(future_time))
    
#     # Structure predictions
#     predictions = []
#     for i in range(len(future_time)):
#         predictions.append({
#             "timestamp_utc": future_time[i].isoformat(),
#             "predicted_price": round(predicted_prices[i], 2),
#             "confidence_interval": confidence_intervals[i],
#             "confidence_percentage": round(confidence_percentage[i], 2)
#         })
    
#     # **Final response format**
#     response = {
#         "symbol": symbol,
#         "run_time_utc": run_time_utc,
#         "actual_live_price": round(last_price, 2),  # Live BTC price from Binance
#         "predictions": predictions
#     }
    
#     return response



###With historical data fetching with SL TP
import requests
import numpy as np
from datetime import datetime, timedelta, timezone

# Binance API Base URL
BINANCE_API_BASE_URL = "https://api.binance.com/api/v3/klines"

def fetch_hourly_candlestick_data(symbol="BTCUSDT"):
    """Fetch the last 24 hours of candlestick data for a given symbol from Binance."""
    url = f"{BINANCE_API_BASE_URL}?symbol={symbol}&interval=15m&limit=96"
    response = requests.get(url)
    data = response.json()
    
    timestamps = [datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc) for entry in data]
    close_prices = [float(entry[4]) for entry in data]
    
    historical_data = [
        {
            "timestamp_utc": timestamps[i].isoformat(),
            "open": float(data[i][1]),
            "high": float(data[i][2]),
            "low": float(data[i][3]),
            "close": close_prices[i]
        } for i in range(len(data))
    ]
    
    return timestamps, close_prices, historical_data

def predict_prices(last_price, last_time):
    """Predict prices for the next 1 hour in 15-minute intervals."""
    
    # Generate future timestamps (every 15 minutes for 1 hour)
    future_time = [last_time + timedelta(minutes=i) for i in range(0, 76, 15)]  # 0 to 75 min
    
    predicted_prices = list(last_price + np.cumsum(np.random.uniform(-50, 50, size=6)))
    
    # Generate confidence intervals
    confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=6)
    confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=6)
    confidence_intervals = [(round(l, 2), round(u, 2)) for l, u in zip(confidence_lower, confidence_upper)]
    
    # Generate TP1, TP2, and SL
    tp1 = [last_price + (abs(p - last_price) * 0.5 if p > last_price else -abs(p - last_price) * 0.5) for p in predicted_prices]
    tp2 = [last_price + (abs(p - last_price) * 1.0 if p > last_price else -abs(p - last_price) * 1.0) for p in predicted_prices]
    sl = [last_price - (abs(p - last_price) * 0.5 if p > last_price else -abs(p - last_price) * 0.5) for p in predicted_prices]

    return future_time, predicted_prices, confidence_intervals, tp1, tp2, sl

def get_crypto_prediction_data(symbol="BTCUSDT"):
    """Fetch cryptocurrency data, predict future prices, and return structured data."""
    
    # Fetch live data for the given symbol
    timestamps, close_prices, historical_data = fetch_hourly_candlestick_data(symbol)
    
    # Get last actual price and time
    last_time = timestamps[-1]
    last_price = close_prices[-1]
    
    # Get current UTC time
    run_time_utc = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    # Predict future prices
    future_time, predicted_prices, confidence_intervals, tp1, tp2, sl = predict_prices(last_price, last_time)

    # Generate confidence percentage (mock data for now)
    confidence_percentage = np.random.uniform(80, 95, size=len(future_time))
    
    # Structure predictions
    predictions = []
    for i in range(len(future_time)):
        predictions.append({
            "timestamp_utc": future_time[i].isoformat(),
            "predicted_price": round(predicted_prices[i], 2),
            "confidence_interval": confidence_intervals[i],
            "confidence_percentage": round(confidence_percentage[i], 2),
            "tp1": round(tp1[i], 2),
            "tp2": round(tp2[i], 2),
            "sl": round(sl[i], 2)
        })
    
    # **Final response format**
    response = {
        "symbol": symbol,
        "run_time_utc": run_time_utc,
        "actual_live_price": round(last_price, 2),  # Live BTC price from Binance
        "historical_data": historical_data,  # 24-hour historical data
        "predictions": predictions
    }
    
    return response