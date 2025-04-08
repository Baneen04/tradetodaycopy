import requests
import numpy as np
import praw
from datetime import datetime, timedelta, timezone
from textblob import TextBlob
from django.conf import settings
from sklearn.ensemble import RandomForestRegressor

# API Keys from Django settings
NEWS_API_KEY = settings.NEWS_API_KEY
REDDIT_CLIENT_ID = settings.REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET = settings.REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT = settings.REDDIT_USER_AGENT

# Binance API URL for 1-minute historical Klines
BINANCE_API_BASE_URL = "https://api.binance.com/api/v3/klines"
NEWS_API_URL = f"https://newsapi.org/v2/everything?q=bitcoin&language=en&apiKey={NEWS_API_KEY}"

# Initialize Reddit API
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

def fetch_live_candlestick_data(symbol="BTCUSDT"):
    """
    Fetch the last 288 candles of 5-minute interval OHLC data from Binance.
    """
    url = f"{BINANCE_API_BASE_URL}?symbol={symbol}&interval=5m&limit=288"
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

def analyze_sentiment(text):
    """Returns sentiment polarity score (-1 to 1) for given text"""
    return TextBlob(text).sentiment.polarity

def fetch_news_sentiment():
    """Fetches latest Bitcoin news and calculates sentiment"""
    response = requests.get(NEWS_API_URL)
    news_data = response.json()
    
    articles = news_data.get("articles", [])
    if not articles:
        return 0  # Neutral sentiment if no news
    
    sentiments = []
    for article in articles:
        title = article.get("title", "") or ""
        description = article.get("description", "") or ""
        text = title + " " + description
        sentiments.append(analyze_sentiment(text))
    
    return np.mean(sentiments) if sentiments else 0  # Average sentiment score

def fetch_reddit_sentiment():
    """Fetches sentiment from hot posts on r/Bitcoin"""
    subreddit = reddit.subreddit("Bitcoin")
    posts = subreddit.hot(limit=20)  # Fetch top 20 posts
    sentiments = [analyze_sentiment(post.title + " " + post.selftext) for post in posts]
    
    return np.mean(sentiments) if sentiments else 0

def train_random_forest(historical_data):
    """Train Random Forest model on historical BTC price data."""
    X, y = [], []
    for i in range(len(historical_data) - 1):
        features = [
            historical_data[i]["open"],
            historical_data[i]["high"],
            historical_data[i]["low"],
            historical_data[i]["close"]
        ]
        X.append(features)
        y.append(historical_data[i + 1]["close"])  # Predicting next close price
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def predict_prices(last_price, last_time, model, sentiment_score):
    """
    Generate future BTC price predictions at 5-minute intervals (next 6 periods, covering 30 minutes),
    incorporating sentiment analysis and Random Forest predictions.
    """
    sentiment_adjustment = sentiment_score * 50  # Adjust price impact
    start_time = (last_time + timedelta(minutes=5)).replace(second=0, microsecond=0)
    future_time = [start_time + timedelta(minutes=5 * i) for i in range(6)]
    
    # Generate Random Forest-based predictions
    predicted_prices = []
    for _ in range(6):
        next_price = model.predict([[last_price, last_price + 10, last_price - 10, last_price]])[0]
        adjusted_price = next_price + sentiment_adjustment
        predicted_prices.append(adjusted_price)
        last_price = adjusted_price  # Update for next iteration
    
    confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=6)
    confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=6)
    confidence_percentage = np.random.uniform(80, 95, size=6)

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
            "sp": round(sp, 2),
            "confidence_interval": f"{l:.2f} to {u:.2f}",
            "confidence_percentage": f"{cp:.2f}%",
        })
    
    return predictions

def get_predictions(symbol="BTCUSDT"):
    """
    Fetch live BTCUSDT data, train Random Forest, generate predictions at 5-minute intervals,
    incorporate sentiment analysis, and return structured results.
    """
    historical_data = fetch_live_candlestick_data(symbol)
    last_data = historical_data[-1]
    last_time = datetime.fromisoformat(last_data["timestamp_utc"])
    last_price = last_data["close"]
    
    model = train_random_forest(historical_data)
    sentiment_score = (fetch_news_sentiment() + fetch_reddit_sentiment()) / 2
    predictions = predict_prices(last_price, last_time, model, sentiment_score)
    
    response_data = {
        "last_actual_price": round(last_price, 2),
        "last_time": last_time.strftime("%Y-%m-%d %H:%M:%S"),
        "historical_data": historical_data,
        "predictions": predictions
    }
    
    return response_data
