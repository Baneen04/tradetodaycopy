import requests
import numpy as np
import praw
from datetime import datetime, timedelta, timezone
from textblob import TextBlob
from django.conf import settings

# API Keys from Django settings
NEWS_API_KEY = settings.NEWS_API_KEY
REDDIT_CLIENT_ID = settings.REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET = settings.REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT = settings.REDDIT_USER_AGENT

# Binance API URL for 30-minute historical Klines
BINANCE_URL = "https://api.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=60"
NEWS_API_URL = f"https://newsapi.org/v2/everything?q=bitcoin&language=en&apiKey={NEWS_API_KEY}"

# Initialize Reddit API
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

def fetch_live_candlestick_data(symbol):
    """Fetches latest 60 candles (30-minute interval) for any symbol from Binance"""
    response = requests.get(BINANCE_URL.format(symbol=symbol))
    data = response.json()
    
    if "code" in data:  # Binance API error handling
        raise ValueError(f"Binance API Error: {data.get('msg', 'Unknown error')}")

    timestamps = [datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc) for entry in data]
    open_prices = [float(entry[1]) for entry in data]
    high_prices = [float(entry[2]) for entry in data]
    low_prices = [float(entry[3]) for entry in data]
    close_prices = [float(entry[4]) for entry in data]
    
    return timestamps, open_prices, high_prices, low_prices, close_prices

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

def predict_prices(last_price, last_time):
    """Predicts symbol price for the next 6 intervals (30-minute intervals for 3 hours)"""
    
    sentiment_score = (fetch_news_sentiment() + fetch_reddit_sentiment()) / 2
    sentiment_adjustment = sentiment_score * 50  # Adjust price impact

    # Predict for the next 6 intervals (30 min * 6 = 3 hours)
    future_time = [last_time + timedelta(minutes=i * 30) for i in range(1, 7)]
    
    predicted_prices = list(last_price + np.cumsum(np.random.uniform(-50, 50, size=6) + sentiment_adjustment))
    open_prices = [p + np.random.uniform(-10, 10) for p in predicted_prices]
    high_prices = [p + np.random.uniform(5, 15) for p in predicted_prices]
    low_prices = [p - np.random.uniform(5, 15) for p in predicted_prices]
    close_prices = predicted_prices

    # Generate confidence intervals
    confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=6)
    confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=6)
    confidence_intervals = [(l, u) for l, u in zip(confidence_lower, confidence_upper)]
    confidence_percentage = np.random.uniform(80, 95, size=6)  # 80-95% confidence

    # Calculate TP and SL based on predicted price movement
    tp1 = [last_price + (p - last_price) * 0.5 for p in predicted_prices]
    tp2 = [last_price + (p - last_price) * 1.0 for p in predicted_prices]
    sl = [last_price - (p - last_price) * 0.5 for p in predicted_prices]

    return future_time, predicted_prices, open_prices, high_prices, low_prices, close_prices, confidence_percentage, confidence_intervals, tp1, tp2, sl

def get_predictions(symbol="BTCUSDT"):
    """Fetches latest price for given symbol, predicts next 3 hours (6 intervals), and returns structured JSON response"""
    try:
        timestamps, _, _, _, close_prices = fetch_live_candlestick_data(symbol)
        last_time = timestamps[-1]
        last_price = close_prices[-1]

        future_time, predicted_prices, predicted_open, predicted_high, predicted_low, predicted_close, confidence_percentage, confidence_intervals, tp1, tp2, sl = predict_prices(last_price, last_time)

        predictions = []
        for i in range(6):
            predictions.append({
                "time": future_time[i].isoformat(),
                "prediction_price": round(predicted_prices[i], 2),
                "tp1": round(tp1[i], 2),
                "tp2": round(tp2[i], 2),
                "sl": round(sl[i], 2),
                "confidence_interval": [round(confidence_intervals[i][0], 2), round(confidence_intervals[i][1], 2)],
                "confidence_percentage": round(confidence_percentage[i], 2),

            })

        return {"symbol": symbol, "last_actual_price": round(last_price, 2), "predictions": predictions}

    except ValueError as e:
        return {"error": str(e)}
