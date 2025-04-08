import time
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from IPython.display import display, clear_output
# Binance API URL for BTC/USDT 1-minute historical Klines
BINANCE_URL = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=60"
# Function to fetch live candlestick data
def fetch_live_candlestick_data():
    response = requests.get(BINANCE_URL)
    data = response.json()
    # Extract relevant data
    timestamps = [datetime.fromtimestamp(entry[0] / 1000) for entry in data]
    open_prices = [float(entry[1]) for entry in data]
    high_prices = [float(entry[2]) for entry in data]
    low_prices = [float(entry[3]) for entry in data]
    close_prices = [float(entry[4]) for entry in data]
    return timestamps, open_prices, high_prices, low_prices, close_prices
# Dummy prediction function (Replace with actual ML model)
def predict_prices(last_price, last_time):
    future_time = [last_time + timedelta(minutes=i) for i in range(1, 16)]
    predicted_prices = [last_price] + list(last_price + np.cumsum(np.random.uniform(-50, 50, size=14)))
    trend_color = 'green' if predicted_prices[-1] > last_price else 'red'
    confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=15)
    confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=15)
    return future_time, predicted_prices, confidence_upper, confidence_lower, trend_color
# Main loop to update graph every 1 minute
while True:
    try:
        # Fetch live data
        timestamps, open_prices, high_prices, low_prices, close_prices = fetch_live_candlestick_data()
        last_time = timestamps[-1]
        last_price = close_prices[-1]
        # Predict next 15 minutes
        future_time, predicted_prices, confidence_upper, confidence_lower, trend_color = predict_prices(last_price, last_time)
        # Create figure
        fig = go.Figure()
        # Candlestick Chart
        fig.add_trace(go.Candlestick(x=timestamps,
                                     open=open_prices,
                                     high=high_prices,
                                     low=low_prices,
                                     close=close_prices,
                                     name="Candlestick"))
        # Confidence Interval (Green for up, Red for down)
        confidence_fill_color = 'rgba(0, 255, 0, 0.2)' if trend_color == 'green' else 'rgba(255, 0, 0, 0.2)'
        fig.add_trace(go.Scatter(x=future_time + future_time[::-1],
                                 y=confidence_upper.tolist() + confidence_lower[::-1].tolist(),
                                 fill='toself',
                                 fillcolor=confidence_fill_color,
                                 line=dict(color='rgba(255,255,255,0)'),
                                 name='Confidence Interval'))
        # Predicted Price Line (Dynamic color)
        predicted_colors = ['lime' if predicted_prices[i] > predicted_prices[i - 1] else 'red' for i in range(1, len(predicted_prices))]
        predicted_colors.insert(0, 'lime' if predicted_prices[0] > last_price else 'red')
        for i in range(len(future_time) - 1):
            fig.add_trace(go.Scatter(
                x=[future_time[i], future_time[i + 1]],
                y=[predicted_prices[i], predicted_prices[i + 1]],
                mode='lines',
                line=dict(color=predicted_colors[i], width=2),
                name="Predicted Price" if i == 0 else "",
                showlegend=(i == 0)
            ))
        # Fix X-Axis: Show time labels including future time & today's date
        min_time = timestamps[0].replace(second=0, microsecond=0)
        max_time = future_time[-1].replace(second=0, microsecond=0)
        time_ticks = pd.date_range(start=min_time, end=max_time, freq='15T')  # 15-minute interval
        fig.update_layout(
            title="BTC/USDT Live Candlestick Chart with Future 15 mins Prediction",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark",
            xaxis=dict(
                tickmode='array',
                tickvals=time_ticks,
                tickformat="%H:%M\n%Y-%m-%d",  # Show both time & date
                rangeslider=dict(visible=False)
            ),
            yaxis=dict(side="right"),
            legend=dict(x=0, y=1, xanchor='left')
        )
        # Display updated graph
        clear_output(wait=True)
        display(fig)
        # Wait for 15 minute before updating
        time.sleep(900)
    except KeyboardInterrupt:
        print("Live update stopped.")
        break