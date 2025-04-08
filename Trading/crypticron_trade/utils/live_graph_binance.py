from binance.client import Client
import pandas as pd
from django.conf import settings

# Get API Keys from Django settings (Avoid crashes if missing)
API_KEY = getattr(settings, "API_KEY", None)
B_SECRET_KEY = getattr(settings, "B_SECRET_KEY", None)

# Initialize Binance Client
client = Client(API_KEY, B_SECRET_KEY)

def fetch_binance_data(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, limit=200):
    """ Fetch live BTC/USDT candlestick data securely from Binance API. """
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)

        # Convert data to DataFrame
        df = pd.DataFrame(klines, columns=[
            "time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_base", "taker_quote", "ignore"
        ])

        # Convert timestamp to datetime
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)

        # Calculate Moving Averages (MA7, MA25, MA99)
        df["MA7"] = df["close"].rolling(window=7, min_periods=1).mean()
        df["MA25"] = df["close"].rolling(window=25, min_periods=1).mean()
        df["MA99"] = df["close"].rolling(window=99, min_periods=1).mean()

        return df
    except Exception as e:
        print(f"❌ Binance API Fetch Error: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure

import plotly.graph_objects as go

def generate_chart():
    """ Generate a Binance-style candlestick chart using Plotly. """
    df = fetch_binance_data()

    if df.empty:
        print("⚠️ No data available for chart.")
        return None  # Return None if no data

    fig = go.Figure()

    # Add Candlestick
    fig.add_trace(go.Candlestick(
        x=df["time"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Candlestick"
    ))

    # Add Moving Averages
    fig.add_trace(go.Scatter(x=df["time"], y=df["MA7"], mode="lines", name="MA7", line=dict(color="yellow")))
    fig.add_trace(go.Scatter(x=df["time"], y=df["MA25"], mode="lines", name="MA25", line=dict(color="pink")))
    fig.add_trace(go.Scatter(x=df["time"], y=df["MA99"], mode="lines", name="MA99", line=dict(color="purple")))

    # Layout
    fig.update_layout(
        title="Live BTC/USDT Candlestick Chart",
        xaxis_title="Time",
        yaxis_title="Price",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        yaxis=dict(side="right"),
        legend=dict(
            x=0,  
            y=1,  
            bgcolor='rgba(255,255,255,0.3)',  
        )
    )
    return fig
