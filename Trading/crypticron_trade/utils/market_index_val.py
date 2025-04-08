import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from binance.client import Client
from matplotlib.patches import Polygon
from scipy.ndimage import gaussian_filter1d
import io
import base64
import time
from django.conf import settings

#Binance key
API_KEY = settings.API_KEY
B_SECRET_KEY= settings.B_SECRET_KEY
client = Client(API_KEY, B_SECRET_KEY)

def get_binance_data_top_100():
    """
    Fetch top 100 Binance symbols by volume and compute their percentage change in price.
    """
    
    tickers = client.get_ticker()
    sorted_tickers = sorted(tickers, key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
    top_symbols = [ticker['symbol'] for ticker in sorted_tickers[:100]]

    data = []
    for symbol in top_symbols:
        try:
            # Get current price
            ticker = client.get_ticker(symbol=symbol)
            current_price = float(ticker['lastPrice'])

            # Get historical price (24 hours ago)
            klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, "24 hours ago UTC", limit=1)
            if klines:
                historical_price = float(klines[0][4])  # Close price
                percent_change = ((current_price - historical_price) / historical_price) * 100
                
                data.append({'symbol': symbol, 'percent_change': percent_change})
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    return pd.DataFrame(data)

def market_prediction_index():
    """
    Compute the Market Prediction Index and return the necessary values for visualization.
    """
    df = get_binance_data_top_100()
    
    if df.empty:
        return None  # Return None if no data available

    # Compute the prediction index (median of percentage changes)
    prediction_line = df['percent_change'].median()
    recommendation = "Sell" if prediction_line < 0 else "Buy"

    # Define histogram bins
    bins = np.linspace(-6, 6, 100)
    hist, bin_edges = np.histogram(df['percent_change'], bins=bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Smooth histogram for a better visual representation
    hist_smooth = gaussian_filter1d(hist, sigma=1.5) * 15

    # Prepare and return relevant data
    return {
        "bin_centers": bin_centers.tolist(),  # Convert NumPy array to list
        "hist_smooth": hist_smooth.tolist(),  # Convert NumPy array to list
        "prediction_line": float(prediction_line),  # Convert NumPy float to Python float
        "recommendation": recommendation
    }

