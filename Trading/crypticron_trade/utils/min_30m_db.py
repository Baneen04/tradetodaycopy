
#with historical data printing

import requests
import numpy as np
import praw
from datetime import datetime, timedelta, timezone
from textblob import TextBlob
from django.conf import settings
from crypticron_trade.models import PredictionResult  # adjust path accordingly
from datetime import timezone
from django.http import JsonResponse

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
        sl = last_price - (diff * 0.5 if p > last_price else -diff * 0.5)

        predictions.append({
            "time": t.strftime("%Y-%m-%d %H:%M:%S"),
            "predicted_price": round(p, 5),
            "tp1": round(tp1, 5),
            "tp2": round(tp2, 5),
            "sp": round(sl, 5),
            "confidence_interval": f"{l:.5f} to {u:.5f}",
            "confidence_percentage": f"{cp:.5f}%",
        })
    
    return predictions
def save30m_predictions(symbol="BTCUSDT"):
    """
    Fetch live BTCUSDT data, generate predictions at 5-minute intervals,
    incorporate sentiment analysis, save the results in MongoDB,
    and return structured results.
    """
    # Fetch the historical candlestick data
    historical_data = fetch_live_candlestick_data(symbol)
    last_data = historical_data[-1]
    last_time = datetime.fromisoformat(last_data["timestamp_utc"])
    last_price = last_data["close"]

    # Generate the price predictions based on the historical data and sentiment analysis
    predictions = predict_prices(last_price, last_time)

    # Prepare the prediction data to save to MongoDB
    prediction_time = "30min"
    timestamps = [datetime.strptime(p["time"], "%Y-%m-%d %H:%M:%S") for p in predictions]
    predicted_prices = [p["predicted_price"] for p in predictions]
    tp1_values = [p["tp1"] for p in predictions]
    tp2_values = [p["tp2"] for p in predictions]
    sl_values = [p["sl"] for p in predictions]
    confidence_intervals = [(p["confidence_interval"].split(" to ")[0], p["confidence_interval"].split(" to ")[1]) for p in predictions]
    confidence_percentages = [float(p["confidence_percentage"].replace("%", "")) for p in predictions]

    # Save the prediction result to MongoDB
    prediction_result = PredictionResult(
        prediction_time=prediction_time,
        symbol=symbol,
        last_actual_price=last_price,
        last_time=last_time,
        timestamps=timestamps,
        predicted_prices=predicted_prices,
        tp1_values=tp1_values,
        tp2_values=tp2_values,
        sl_values=sl_values,
        confidence_intervals=confidence_intervals,
        confidence_percentages=confidence_percentages,
        historical_data=historical_data,
    )
    prediction_result.save()  # Save the prediction to the database


# Function to fetch the latest prediction from the DB
def get_30prediction_from_db(request, symbol="BTCUSDT"):
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