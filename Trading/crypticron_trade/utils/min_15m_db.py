import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from datetime import datetime, timedelta, timezone
from binance.client import Client
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import praw  # Reddit API
from django.conf import settings
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import norm
from crypticron_trade.models import PredictionResult  # adjust path accordingly
from datetime import timezone
from django.http import JsonResponse
# Binance API Keys
API_KEY = settings.API_KEY
B_SECRET_KEY = settings.B_SECRET_KEY
NEWS_API_KEY = settings.NEWS_API_KEY
REDDIT_CLIENT_ID = settings.REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET = settings.REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT = settings.REDDIT_USER_AGENT
client = Client(API_KEY, B_SECRET_KEY)

# Binance Base URL for 1-minute historical data
BINANCE_API_BASE_URL = "https://api.binance.com/api/v3/klines"

# 1️⃣ Fetch 1-Minute Historical Data (24 Hours)
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

# 2️⃣ Fetch 15-Minute Interval Data (3 Hours) for Prediction
def fetch_binance_data(symbol, interval=Client.KLINE_INTERVAL_1MINUTE, lookback="3 hours ago UTC"):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume", 
                                       "close_time", "quote_asset_volume", "number_of_trades", 
                                       "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df[["timestamp", "open", "high", "low", "close"]]

# 3️⃣ Fetch Bitcoin News
def fetch_news():
    url = f"https://newsapi.org/v2/everything?q=bitcoin&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    news_data = response.json()
    if news_data["status"] != "ok":
        return []
    articles = news_data["articles"]
    return [article["title"] + ". " + article["description"] for article in articles if article["description"]]

# 4️⃣ Fetch Reddit Posts
def fetch_reddit():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    subreddit = reddit.subreddit("cryptocurrency")
    return [post.title + ". " + post.selftext for post in subreddit.hot(limit=20)]

# 5️⃣ Sentiment Analysis
def analyze_sentiment(texts):
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(text)["compound"] for text in texts]
    return np.mean(scores) if scores else 0

# 6️⃣ Calculate RSI
def calculate_rsi(df, window=14):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

# 7️⃣ Calculate MACD
def calculate_macd(df):
    short_ema = df["close"].ewm(span=12, adjust=False).mean()
    long_ema = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = short_ema - long_ema
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df

#  Predict BTC Price for Next 15 Minutes
def store_prediction(symbol="BTCUSDT"):
    # Fetch Data
    historical_data = fetch_live_candlestick_data(symbol)  # 1-minute data
    df = fetch_binance_data(symbol)
    df.set_index("timestamp", inplace=True)

    # Feature Engineering
    df["SMA_10"] = df["close"].rolling(window=10).mean()
    df["SMA_50"] = df["close"].rolling(window=50).mean()
    df["EMA_10"] = df["close"].ewm(span=10, adjust=False).mean()
    df["EMA_50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["Volatility"] = df["close"].rolling(window=10).std()

    # Get Sentiment Scores
    news_sentiment = analyze_sentiment(fetch_news())
    reddit_sentiment = analyze_sentiment(fetch_reddit())
    df["News_Sentiment"] = news_sentiment
    df["Reddit_Sentiment"] = reddit_sentiment

    # RSI & MACD
    df = calculate_rsi(df)
    df = calculate_macd(df)

    # Normalize Sentiment Scores
    X = df[["SMA_10", "SMA_50", "EMA_10", "EMA_50", "Volatility", "News_Sentiment", "Reddit_Sentiment", "RSI", "MACD", "Signal"]]
    y = df["close"]

    # Train Random Forest Regressor
    model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X, y)

    # Initialize Variables
    future_prices = []
    future_timestamps = []
    confidence_intervals = []
    current_features = pd.DataFrame([X.iloc[-1]], columns=X.columns)
    current_time = df.index[-1]
    errors_so_far = list(abs(y - model.predict(X)))

    # Prediction Loop for the next 15 minutes
    for i in range(15):
        predicted_price = model.predict(pd.DataFrame(current_features, columns=X.columns))[0]

        if len(errors_so_far) >= 15:
            rolling_std = np.std(errors_so_far[-15:])
            margin_of_error = 1.96 * rolling_std
            lower_bound = predicted_price - margin_of_error
            upper_bound = predicted_price + margin_of_error
            confidence = 100 - (rolling_std / predicted_price * 100)
        else:
            lower_bound, upper_bound, confidence = predicted_price, predicted_price, 100

        # Store Prediction Results
        future_timestamps.append(current_time + timedelta(minutes=1))
        future_prices.append(predicted_price)
        confidence_intervals.append((lower_bound, upper_bound, confidence))

        # Update errors dynamically
        if i > 0:
            errors_so_far.append(abs(future_prices[-1] - predicted_price))

        # Update Features for Next Iteration
        new_features = current_features.copy()
        new_features.iloc[0, :-1] = new_features.iloc[0, 1:].values
        new_features.iloc[0, -1] = predicted_price
        current_features = new_features.copy()

        # Increment Time for Next Prediction
        current_time += timedelta(minutes=1)

    # Define the last price and calculate TP1, TP2, and SL
    last_price = df["close"].iloc[-1]
    tp1_values = [last_price + (abs(pred - last_price) * 0.5) for pred in future_prices]
    tp2_values = [last_price + (abs(pred - last_price) * 1.0) for pred in future_prices]
    sl_values = [last_price - (abs(pred - last_price) * 0.5) for pred in future_prices]

    # Prepare Data for DB Saving
    prediction_time = "15min"
    timestamps = future_timestamps
    predicted_prices = future_prices
    confidence_percentages = [conf for _, _, conf in confidence_intervals]
    confidence_intervals = [[float(i) for i in p.split(" to ")] for p in [f"{lower} to {upper}" for lower, upper, _ in confidence_intervals]]

    # Save to MongoDB using MongoEngine's save method
    prediction_result = PredictionResult(
        prediction_time=prediction_time,
        symbol=symbol,
        last_actual_price=last_price,
        last_time=datetime.strptime(historical_data[-1]["timestamp_utc"], "%Y-%m-%dT%H:%M:%S%z"),
        timestamps=timestamps,
        predicted_prices=predicted_prices,
        tp1_values=tp1_values,
        tp2_values=tp2_values,
        sl_values=sl_values,
        confidence_intervals=confidence_intervals,
        confidence_percentages=confidence_percentages,
        historical_data=historical_data,
    )
    prediction_result.save()  # Save to the database



# Function to fetch the latest prediction from the DB
def get_prediction_from_db(request, symbol="BTCUSDT"):
    # Query for the most recent prediction
    prediction = PredictionResult.objects(symbol=symbol).order_by("-created_at").first()

    if not prediction:
        return JsonResponse({"error": "No prediction found"}, status=404)

    # Prepare predictions list to return in response
    predictions = []
    for i in range(len(prediction.timestamps)):
        predictions.append({
            "time": prediction.timestamps[i].strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_price": round(prediction.predicted_prices[i], 5),
            "tp1": round(prediction.tp1_values[i], 5),
            "tp2": round(prediction.tp2_values[i], 5),
            "sl": round(prediction.sl_values[i], 5),
            "confidence_interval": f"{prediction.confidence_intervals[i][0]:.5f} to {prediction.confidence_intervals[i][1]:.5f}",
            "confidence_percentage": f"{prediction.confidence_percentages[i]:.5f}%"
        })

    return ({
        "symbol": prediction.symbol,
        "last_actual_price": float(prediction.last_actual_price),
        "last_time": prediction.last_time.isoformat(),
        "historical_data": prediction.historical_data,
        "predictions": predictions
    })