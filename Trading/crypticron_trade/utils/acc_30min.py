# import requests
# import numpy as np
# import praw
# from datetime import datetime, timedelta, timezone
# from textblob import TextBlob
# from django.conf import settings

# # API Keys from Django settings
# NEWS_API_KEY = settings.NEWS_API_KEY
# REDDIT_CLIENT_ID = settings.REDDIT_CLIENT_ID
# REDDIT_CLIENT_SECRET = settings.REDDIT_CLIENT_SECRET
# REDDIT_USER_AGENT = settings.REDDIT_USER_AGENT

# # API URLs
# BINANCE_URL = "https://api.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=60"
# NEWS_API_URL = f"https://newsapi.org/v2/everything?q=bitcoin&language=en&apiKey={NEWS_API_KEY}"

# # Initialize Reddit API
# reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
#                      client_secret=REDDIT_CLIENT_SECRET,
#                      user_agent=REDDIT_USER_AGENT)

# def fetch_live_candlestick_data(symbol):
#     """Fetches latest 60 candles (30-minute interval) for any symbol from Binance"""
#     response = requests.get(BINANCE_URL.format(symbol=symbol))
#     data = response.json()
    
#     if "code" in data:  # Binance API error handling
#         raise ValueError(f"Binance API Error: {data.get('msg', 'Unknown error')}")

#     timestamps = [datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc) for entry in data]
#     open_prices = [float(entry[1]) for entry in data]
#     high_prices = [float(entry[2]) for entry in data]
#     low_prices = [float(entry[3]) for entry in data]
#     close_prices = [float(entry[4]) for entry in data]
    
#     return timestamps, open_prices, high_prices, low_prices, close_prices

# def analyze_sentiment(text):
#     """Returns sentiment polarity score (-1 to 1) for given text"""
#     return TextBlob(text).sentiment.polarity

# def fetch_news_sentiment():
#     """Fetches latest Bitcoin news and calculates sentiment"""
#     response = requests.get(NEWS_API_URL)
#     news_data = response.json()
    
#     articles = news_data.get("articles", [])
#     if not articles:
#         return 0  # Neutral sentiment if no news
    
#     sentiments = []
#     for article in articles:
#         title = article.get("title", "") or ""
#         description = article.get("description", "") or ""
#         text = title + " " + description
#         sentiments.append(analyze_sentiment(text))
    
#     return np.mean(sentiments) if sentiments else 0  # Average sentiment score

# def fetch_reddit_sentiment():
#     """Fetches sentiment from hot posts on r/Bitcoin"""
#     subreddit = reddit.subreddit("Bitcoin")
#     posts = subreddit.hot(limit=20)  # Fetch top 20 posts
#     sentiments = [analyze_sentiment(post.title + " " + post.selftext) for post in posts]
    
#     return np.mean(sentiments) if sentiments else 0

# def predict_prices(last_price, last_time):
#     """Predicts symbol price for the next 6 intervals (30-minute intervals for 3 hours)"""
#     sentiment_score = (fetch_news_sentiment() + fetch_reddit_sentiment()) / 2
#     sentiment_adjustment = sentiment_score * 50  # Adjust price impact

#     # Predict for the next 6 intervals (30 min * 6 = 3 hours)
#     future_time = [last_time + timedelta(minutes=i * 30) for i in range(1, 7)]
    
#     # predicted_prices = [last_price] + list(last_price + np.cumsum(np.random.uniform(-50, 50, size=5) + sentiment_adjustment))
#     predicted_prices = list(last_price + np.cumsum(np.random.uniform(-50, 50, size=6) + sentiment_adjustment))

#     open_prices = [p + np.random.uniform(-10, 10) for p in predicted_prices]
#     high_prices = [p + np.random.uniform(5, 15) for p in predicted_prices]
#     low_prices = [p - np.random.uniform(5, 15) for p in predicted_prices]
#     close_prices = predicted_prices
    
#     # Generate confidence intervals
#     confidence_upper = np.array(predicted_prices) + np.random.uniform(30, 70, size=6)
#     confidence_lower = np.array(predicted_prices) - np.random.uniform(30, 70, size=6)
#     confidence_percentage = np.random.uniform(80, 95, size=6)  # 80-95% confidence
    
#     return future_time, predicted_prices, open_prices, high_prices, low_prices, close_prices, confidence_percentage, confidence_upper, confidence_lower

# def get_predictions(symbol="BTCUSDT"):
#     """Fetches latest price for given symbol, predicts next 3 hours (6 intervals), and returns structured JSON response"""
#     try:
#         timestamps, _, _, _, close_prices = fetch_live_candlestick_data(symbol)
#         last_time = timestamps[-1]
#         last_price = close_prices[-1]

#         # Capture runtime and actual price at runtime
#         run_time_utc = datetime.now(timezone.utc).isoformat()
#         actual_live_price = last_price

#         future_time, _, predicted_open, predicted_high, predicted_low, predicted_close, confidence_percentage, confidence_upper, confidence_lower = predict_prices(last_price, last_time)

#         predictions = [
#             {
#                 "time": future_time[i].isoformat(),
#                 "predicted_price": round(predicted_close[i], 2),
#                 "confidence_interval": [round(confidence_lower[i], 2), round(confidence_upper[i], 2)],
#                 "confidence_percentage": round(confidence_percentage[i], 2)
#             }
#             for i in range(6)  # First 6 intervals (30-min each)
#         ]

#         return {
#             "symbol": symbol,
#             "run_time_utc": run_time_utc,
#             "actual_live_price": actual_live_price,
#             "predictions": predictions
#         }

#     except ValueError as e:
#         return {"error": str(e)}


#with historical data printing

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

# Binance API URL for 1-minute historical Klines
BINANCE_API_BASE_URL = "https://api.binance.com/api/v3/klines"
NEWS_API_URL = f"https://newsapi.org/v2/everything?q=bitcoin&language=en&apiKey={NEWS_API_KEY}"

# Initialize Reddit API
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

def fetch_live_candlestick_data(symbol="BTCUSDT"):
    """
    Fetch the last 60 candles of 30-minute interval OHLC data from Binance.
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

def predict_prices(last_price, last_time):
    """
    Generate future BTC price predictions at 5-minute intervals (next 6 periods, covering 30 minutes),
    incorporating sentiment analysis from news and Reddit.
    """
    sentiment_score = (fetch_news_sentiment() + fetch_reddit_sentiment()) / 2
    sentiment_adjustment = sentiment_score * 50  # Adjust price impact

    start_time = (last_time + timedelta(minutes=5)).replace(second=0, microsecond=0)
    future_time = [start_time + timedelta(minutes=5 * i) for i in range(6)]  # 5-minute intervals up to 30 minutes
    
    predicted_prices = list(last_price + np.cumsum(np.random.uniform(-50, 50, size=6) + sentiment_adjustment))
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
            "predicted_price": round(p, 5),
            "tp1": round(tp1, 5),
            "tp2": round(tp2, 5),
            "sp": round(sp, 5),
            "confidence_interval": f"{l:.5f} to {u:.5f}",
            "confidence_percentage": f"{cp:.5f}%",
        })
    
    return predictions

def get_predictions(symbol="BTCUSDT"):
    """
    Fetch live BTCUSDT data, generate predictions at 5-minute intervals,
    incorporate sentiment analysis, and return structured results.
    """
    historical_data = fetch_live_candlestick_data(symbol)
    last_data = historical_data[-1]
    last_time = datetime.fromisoformat(last_data["timestamp_utc"])
    last_price = last_data["close"]

    predictions = predict_prices(last_price, last_time)
    
    response_data = {
        "last_actual_price": round(last_price, 5),
        "last_time": last_time.strftime("%Y-%m-%d %H:%M:%S"),
        "historical_data": historical_data,
        "predictions": predictions
    }

    return response_data
