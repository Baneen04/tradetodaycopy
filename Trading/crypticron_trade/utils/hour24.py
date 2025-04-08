import jax
import jax.numpy as jnp
import optax
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import praw
from binance.client import Client
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta, timezone
from django.conf import settings
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Binance API Configuration
BINANCE_API_BASE_URL = "https://api.binance.com/api/v3/klines"
API_KEY = settings.API_KEY
B_SECRET_KEY = settings.B_SECRET_KEY
NEWS_API_KEY = settings.NEWS_API_KEY
REDDIT_CLIENT_ID = settings.REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET = settings.REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT = settings.REDDIT_USER_AGENT
client = Client(API_KEY, B_SECRET_KEY)

def fetch_hourly_candlestick_data(symbol="BTCUSDT"):
    """Fetch the last 24 hours of candlestick data for a given symbol from Binance."""
    url = f"{BINANCE_API_BASE_URL}?symbol={symbol}&interval=1h&limit=24"
    response = requests.get(url)
    data = response.json()
    
    timestamps = [datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc) for entry in data]
    historical_data = [
        {
            "timestamp_utc": timestamps[i].isoformat(),
            "open": float(data[i][1]),
            "high": float(data[i][2]),
            "low": float(data[i][3]),
            "close": float(data[i][4])
        } for i in range(len(data))
    ]
    
    return historical_data

def fetch_binance_data(symbol, interval=Client.KLINE_INTERVAL_1HOUR, lookback="144 hours ago UTC"):
    """Fetch historical Binance data."""
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df[["timestamp", "close"]]

def fetch_news():
    """Fetch Bitcoin-related news."""
    url = f"https://newsapi.org/v2/everything?q=bitcoin&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    news_data = response.json()
    return [article["title"] + ". " + article["description"] for article in news_data.get("articles", []) if article.get("description")]

def fetch_reddit():
    """Fetch Reddit cryptocurrency discussions."""
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
    subreddit = reddit.subreddit("cryptocurrency")
    return [post.title + ". " + post.selftext for post in subreddit.hot(limit=20)]

def analyze_sentiment(texts):
    """Perform sentiment analysis."""
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(text)["compound"] for text in texts]
    return np.mean(scores) if scores else 0

def prepare_data(df, lookback=60):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[['close']])
    X, y = [], []
    for i in range(lookback, len(scaled_data) - 24):  # Ensure y has 24 elements
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i:i+24, 0])  # Now predicting 24 steps
    return jnp.array(X).reshape((len(X), lookback, 1)), jnp.array(y), scaler


# def create_model(params, x):
#     x = x.reshape(x.shape[0], -1)
#     for w, b in params[:-1]:
#         x = jax.nn.relu(jnp.dot(x, w) + b)
#     w, b = params[-1]
#     return jnp.dot(x, w) + b

def create_model(params, x):
    x = x.reshape(x.shape[0], -1)
    # print(f"Input shape to model: {x.shape}")  # Debugging
    for w, b in params[:-1]:
        x = jax.nn.relu(jnp.dot(x, w) + b)
    w, b = params[-1]
    output = jnp.dot(x, w) + b
    # print(f"Output shape from model: {output.shape}")  # Debugging
    return output


def init_params(layer_sizes, key):
    """Initialize model parameters."""
    keys = jax.random.split(key, len(layer_sizes))
    return [(jax.random.normal(keys[i], (layer_sizes[i], layer_sizes[i+1])) * 0.01, jnp.zeros(layer_sizes[i+1])) for i in range(len(layer_sizes)-1)]

def loss_fn(params, x, y):
    """Loss function for training."""
    preds = create_model(params, x)
    return jnp.mean((preds - y) ** 2)

optimizer = optax.adam(learning_rate=0.001)

@jax.jit
def train_step(params, opt_state, x, y):
    loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
    updates, opt_state = optimizer.update(grads, opt_state, params)
    params = optax.apply_updates(params, updates)
    return params, opt_state, loss

def predict_symbol_24h(symbol):
    # _, historical_data = fetch_hourly_candlestick_data(symbol)
    df = fetch_binance_data(symbol)
    df.set_index("timestamp", inplace=True)
    df["SMA_10"] = df["close"].rolling(window=10, min_periods=1).mean()
    df["SMA_50"] = df["close"].rolling(window=50, min_periods=1).mean()
    df["EMA_10"] = df["close"].ewm(span=10, adjust=False, min_periods=1).mean()
    df["EMA_50"] = df["close"].ewm(span=50, adjust=False, min_periods=1).mean()
    df["Volatility"] = df["close"].rolling(window=10, min_periods=1).std()


    # print(df.tail(10))  # See the last 10 rows before dropna()

    df.dropna(inplace=True)
    # print("After dropping NaN:", df.shape)

    # Sentiment Analysis
    news_sentiment = analyze_sentiment(fetch_news())
    reddit_sentiment = analyze_sentiment(fetch_reddit())
    df["News_Sentiment"] = news_sentiment
    df["Reddit_Sentiment"] = reddit_sentiment

    X, y, scaler = prepare_data(df)
    # print(X)
 
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    key = jax.random.PRNGKey(0)
    # layer_sizes = [lookback, 64, 32, 4]
    layer_sizes = [X_train.shape[1], 64, 32, 24]
    params = init_params(layer_sizes, key)
    
    # Set up optimizer
    opt_state = optimizer.init(params)

    # Train model
    epochs = 20
    batch_size = 32
    for epoch in range(epochs):
        for i in range(0, len(X_train), batch_size):
            X_batch = X_train[i:i + batch_size]
            y_batch = y_train[i:i + batch_size]
            params, opt_state, loss = train_step(params, opt_state, X_batch, y_batch)

    # Generate predictions
    last_sequence = X[-1].reshape(1, X.shape[1], 1)
    # predicted_scaled = create_model(params, last_sequence)
    # predicted_prices = scaler.inverse_transform(predicted_scaled.reshape(1, -1))[0]
    predicted_prices = create_model(params, last_sequence).reshape(-1)
    predicted_scaled = create_model(params, last_sequence)
    # print(f"Predicted output shape: {predicted_scaled.shape}")  # Ensure it is (1,24) or (24,)

    if predicted_prices.shape[0] < 24:
        predicted_prices = np.pad(predicted_prices, (0, 24 - predicted_prices.shape[0]), mode='edge')
    predicted_prices = scaler.inverse_transform(predicted_prices.reshape(1, -1))[0]

    # Convert to Python floats
    predicted_prices = [float(price) for price in predicted_prices]
    last_price = df['close'].iloc[-1]
    last_time = df.index[-1]
    future_timestamps = [last_time + timedelta(hours=i) for i in range(1, 25)]
    
    actual_prices = scaler.inverse_transform(y_test[:1].reshape(1, -1))[0]
    errors = np.abs(predicted_prices - actual_prices)
    mape = np.mean((errors / actual_prices) * 100)
    confidence_percent = max(100 - mape, 50)  # Ensuring a minimum confidence of 50%
    confidence_range = float(np.std(errors))  # Convert NumPy float to Python float

    # confidence_range = np.std(predicted_prices - y[-1].numpy())
    # confidence_range = np.std(predicted_prices - np.array(y[-1]))
    # confidence_percent = max(100 - np.mean(abs(predicted_prices - np.array(y[-1])) / np.array(y[-1]) * 100), 50)
    historical_data = fetch_hourly_candlestick_data(symbol)  # 1-minute data
    predictions = []
    for i, timestamp in enumerate(future_timestamps):
        price = predicted_prices[i] 
        diff = abs(price - last_price)
        tp1 = last_price + (diff * 0.5 if price > last_price else -diff * 0.5)
        tp2 = last_price + (diff * 1.0 if price > last_price else -diff * 1.0)
        sl = last_price - (diff * 0.5 if price > last_price else -diff * 0.5)
        lower_bound = predicted_prices[i] - confidence_range
        upper_bound = predicted_prices[i] + confidence_range
        predictions.append({
            "time": timestamp.isoformat(),
            "predicted_price": f"${price:,.2f}",
            "confidence_interval": f"${lower_bound:.2f} - ${upper_bound:.2f}",
            "confidence_percentage": f"{confidence_percent:.2f}%",
            "tp1": round(tp1, 2),
            "tp2": round(tp2, 2),
            "sl": round(sl, 2),
        })
    
    return {
        "last_actual_price": f"${last_price:,.2f}",
        "last_time": last_time.isoformat(),
        "historical_data": historical_data,
        "predictions": predictions
    }
