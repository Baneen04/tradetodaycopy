import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta, timezone
from binance.client import Client
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import praw  # Reddit API
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from django.conf import settings

#Binance key
API_KEY = settings.API_KEY
B_SECRET_KEY= settings.B_SECRET_KEY
NEWS_API_KEY = settings.NEWS_API_KEY
#REDDIT KEY
REDDIT_CLIENT_ID= settings.REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET = settings.REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT = settings.REDDIT_USER_AGENT

# Binance API Keys
client = Client(API_KEY, B_SECRET_KEY)

# Fetch BTCUSDT 1-minute historical data
def fetch_binance_data(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, lookback="3 hours ago UTC"):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df[["timestamp", "close"]]

# Fetch Bitcoin News
def fetch_news():
    url = f"https://newsapi.org/v2/everything?q=bitcoin&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    news_data = response.json()
    if news_data["status"] != "ok":
        return []
    articles = news_data["articles"]
    return [article["title"] + ". " + article["description"] for article in articles if article["description"]]

# Fetch Reddit Posts
def fetch_reddit():
    reddit = praw.Reddit(
        client_id= REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent= REDDIT_CLIENT_ID)
    subreddit = reddit.subreddit("cryptocurrency")
    return [post.title + ". " + post.selftext for post in subreddit.hot(limit=20)]

# Sentiment Analysis
def analyze_sentiment(texts):
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(text)["compound"] for text in texts]
    return np.mean(scores) if scores else 0

# Load Data
# Main Prediction Function
def predict_btc_15():
    df = fetch_binance_data()
    df.set_index("timestamp", inplace=True)

    # Feature Engineering
    df["SMA_10"] = df["close"].rolling(window=10).mean()
    df["SMA_50"] = df["close"].rolling(window=50).mean()
    df["EMA_10"] = df["close"].ewm(span=10, adjust=False).mean()
    df["EMA_50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["Volatility"] = df["close"].rolling(window=10).std()
    df.dropna(inplace=True)

    # Get Sentiment Scores
    news_sentiment = analyze_sentiment(fetch_news())
    reddit_sentiment = analyze_sentiment(fetch_reddit())
    df["News_Sentiment"] = news_sentiment
    df["Reddit_Sentiment"] = reddit_sentiment

    # Train Model
    X = df[["SMA_10", "SMA_50", "EMA_10", "EMA_50", "Volatility", "News_Sentiment", "Reddit_Sentiment"]]
    y = df["close"]
    model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X, y)

    # Predict Next 15 Minutes
    # Prediction Loop
    future_prices = []
    future_timestamps = []
    confidence_intervals = []
    current_features = pd.DataFrame([X.iloc[-1]], columns=X.columns)
    current_time = df.index[-1]

    # Store errors for confidence calculation
    errors_so_far = list(abs(y - model.predict(X)))

    for i in range(15):
        predicted_price = model.predict(pd.DataFrame(current_features, columns=X.columns))[0]

        # Ensure we have enough errors for confidence calculation
        if len(errors_so_far) >= 10:
            rolling_std = np.std(errors_so_far[-10:])  # Use last 10 errors
            margin_of_error = 1.96 * rolling_std
            lower_bound = predicted_price - margin_of_error
            upper_bound = predicted_price + margin_of_error
            confidence = 100 - (rolling_std / predicted_price * 100)
        else:
            lower_bound, upper_bound, confidence = predicted_price, predicted_price, 100  # Default confidence

        # Store results
        future_timestamps.append(current_time)
        future_prices.append(predicted_price)
        confidence_intervals.append((lower_bound, upper_bound, confidence))

        # Update errors dynamically
        if i > 0:
            errors_so_far.append(abs(future_prices[-1] - predicted_price))

        # 🔹 **Fix: Update Features Properly for Next Step**
        new_features = current_features.copy()
        new_features.iloc[0, :-1] = new_features.iloc[0, 1:].values  # Shift previous values
        new_features.iloc[0, -1] = predicted_price  # Set last value to predicted price
        current_features = new_features.copy()  # Update for next iteration
        
        current_time += timedelta(minutes=1)


    # Generate Graph
    graph_path = os.path.join(settings.MEDIA_ROOT, "15min_prediction.png")
    
    plt.figure(figsize=(12, 6))

    # Define the split for 70% actual, 30% predicted
    total_points = len(df) + len(future_timestamps)
    actual_points = int(0.5 * total_points)  # 70% of the total points
    predicted_points = total_points - actual_points  # 30% for predictions

    # Get last 70% actual prices
    actual_timestamps = df.index[-actual_points:]
    actual_prices = df["close"].iloc[-actual_points:]

    # Append last actual price to predicted data for smooth transition
    all_timestamps = list(actual_timestamps) + future_timestamps
    all_prices = list(actual_prices) + future_prices

    # Plot actual prices (Blue, Solid Line)
    plt.plot(actual_timestamps, actual_prices, color="blue", marker="o", linestyle="-", label="Actual Prices")

    # Plot predicted prices (Red, Dashed Line)
    plt.plot(future_timestamps, future_prices, color="red", marker="o", linestyle="--", label="Predicted Prices")

    # Add label only to the last predicted value
    last_predicted_time = future_timestamps[-1]
    last_predicted_price = future_prices[-1]
    plt.text(last_predicted_time, last_predicted_price, f"{last_predicted_price:.2f}",
            fontsize=12, ha='left', color="red", fontweight="bold")

    # Formatting X-Axis
    plt.xlabel("Time (UTC)", fontsize=12)
    plt.ylabel("BTC Price (USDT)", fontsize=12)
    plt.title("BTC Price Prediction (70% Actual, 30% Predicted)", fontsize=14)

    # Rotate x-ticks and set 15-minute intervals
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=15))  # Set interval to 15 min
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))  # Format as HH:MM

    # Ensure the directory exists
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    # Save graph
    plt.savefig(graph_path)
    plt.close()

    return {
        "predictions": [
            {
                "time": str(time),
                "predicted_price": f"${price:,.2f}",
                "confidence": f"{confidence:.2f}%",
                "range": f"${lower:.2f} - ${upper:.2f}"
            }
            for time, price, (lower, upper, confidence) in zip(future_timestamps, future_prices, confidence_intervals)
        ],
        "last_actual_price": f"${df['close'].iloc[-1]:,.2f}",
        "graph_url": "/media/15min_prediction.png"  # URL to access graph
    }