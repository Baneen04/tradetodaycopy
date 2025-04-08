import os
import jax
import jax.numpy as jnp
import optax
import numpy as np
import pandas as pd
import ccxt
import requests
import praw
import matplotlib.pyplot as plt
from binance.client import Client
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from django.conf import settings
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Binance API Keys
API_KEY = settings.API_KEY
B_SECRET_KEY = settings.B_SECRET_KEY
NEWS_API_KEY = settings.NEWS_API_KEY
REDDIT_CLIENT_ID = settings.REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET = settings.REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT = settings.REDDIT_USER_AGENT

client = Client(API_KEY, B_SECRET_KEY)

# Fetch BTCUSDT data from Binance
def fetch_binance_data(symbol, interval=Client.KLINE_INTERVAL_1MINUTE, lookback="12 hours ago UTC"):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    # print(df)
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
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT)
    subreddit = reddit.subreddit("cryptocurrency")
    return [post.title + ". " + post.selftext for post in subreddit.hot(limit=20)]

# Sentiment Analysis
def analyze_sentiment(texts):
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(text)["compound"] for text in texts]
    return np.mean(scores) if scores else 0

# Prepare Data
def prepare_data(df, lookback=30):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[["close"]])
    
    X, y = [], []
    for i in range(lookback, len(scaled_data) - 30, 10):
        X.append(scaled_data[i - lookback:i, 0])
        y.append([scaled_data[i + 9, 0], scaled_data[i + 19, 0], scaled_data[i + 29, 0]])
    
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], lookback, 1))
    return jnp.array(X), jnp.array(y), scaler

# Define MLP Model
def create_model(params, x):
    x = x.reshape(x.shape[0], -1)
    for w, b in params[:-1]:
        x = jax.nn.relu(jnp.dot(x, w) + b)
    w, b = params[-1]
    return jnp.dot(x, w) + b

# Initialize Model Parameters
def init_params(layer_sizes, key):
    keys = jax.random.split(key, len(layer_sizes))
    params = []
    for i, (in_size, out_size) in enumerate(zip(layer_sizes[:-1], layer_sizes[1:])):
        w = jax.random.normal(keys[i], (in_size, out_size)) * 0.01
        b = jnp.zeros(out_size)
        params.append((w, b))
    return params

# Training Step
optimizer = optax.adam(learning_rate=0.001)
@jax.jit
def train_step(params, opt_state, x, y):
    loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
    updates, opt_state = optimizer.update(grads, opt_state, params)
    params = optax.apply_updates(params, updates)
    return params, opt_state, loss

# Loss Function
def loss_fn(params, x, y):
    preds = create_model(params, x)
    return jnp.mean((preds - y) ** 2)

# Predict  Prices
def predict_symbol_30(symbol):
    df = fetch_binance_data(symbol)
    df.set_index("timestamp", inplace=True)
    
    # Feature Engineering
    df["SMA_10"] = df["close"].rolling(window=10, min_periods=1).mean()
    df["SMA_50"] = df["close"].rolling(window=50, min_periods=1).mean()
    df["EMA_10"] = df["close"].ewm(span=10, adjust=False, min_periods=1).mean()
    df["EMA_50"] = df["close"].ewm(span=50, adjust=False, min_periods=1).mean()
    df["Volatility"] = df["close"].rolling(window=10, min_periods=1).std()

    print(df.tail(10))  # See the last 10 rows before dropna()

    df.dropna(inplace=True)
    print("After dropping NaN:", df.shape)

    # Sentiment Analysis
    news_sentiment = analyze_sentiment(fetch_news())
    reddit_sentiment = analyze_sentiment(fetch_reddit())
    df["News_Sentiment"] = news_sentiment
    df["Reddit_Sentiment"] = reddit_sentiment
    
    X, y, scaler = prepare_data(df)
    # Train-test split
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Initialize model
    key = jax.random.PRNGKey(0)
    layer_sizes = [X_train.shape[1], 64, 32, 3]
    params = init_params(layer_sizes, key)

    # Set up optimizer
    opt_state = optimizer.init(params)

    # Train model
    epochs = 10
    batch_size = 32
    for epoch in range(epochs):
        for i in range(0, len(X_train), batch_size):
            X_batch = X_train[i:i + batch_size]
            y_batch = y_train[i:i + batch_size]
            params, opt_state, loss = train_step(params, opt_state, X_batch, y_batch)

    # Generate predictions
    last_sequence = X[-1].reshape(1, X.shape[1], 1)
    predicted_scaled = create_model(params, last_sequence)
    predicted_prices = scaler.inverse_transform(predicted_scaled.reshape(1, -1))[0]

    # Convert to Python floats
    predicted_prices = [float(price) for price in predicted_prices]

    actual_prices = scaler.inverse_transform(y_test[:1].reshape(1, -1))[0]
    errors = np.abs(predicted_prices - actual_prices)
    mape = np.mean((errors / actual_prices) * 100)
    confidence_percent = max(100 - mape, 50)  # Ensuring a minimum confidence of 50%
    confidence_range = float(np.std(errors))  # Convert NumPy float to Python float

    last_timestamp = df.index[-1]
    future_timestamps = [last_timestamp + timedelta(minutes=i) for i in [10, 20, 30]]

    # Create a formatted response
    predictions = {
        "Predicted Prices (with Confidence Intervals)": []
    }

    for i, timestamp in enumerate(future_timestamps):
        lower_bound = predicted_prices[i] - confidence_range
        upper_bound = predicted_prices[i] + confidence_range
        formatted_prediction = {
            "timestamp": str(timestamp),
            "predicted_price": f"${predicted_prices[i]:,.2f}",
            "confidence": f"{confidence_percent:.2f}%",
            "range": f"${lower_bound:,.2f} - ${upper_bound:,.2f}"
        }
        predictions["Predicted Prices (with Confidence Intervals)"].append(formatted_prediction)

    # Generate and save graph
    generate_graph(symbol,df, future_timestamps, predicted_prices)

    return predictions



# Graph Generation
def generate_graph(symbol, data, future_timestamps, predicted_prices):
    # Path for saving the graph
    graph_path = os.path.join(settings.MEDIA_ROOT, f"{symbol}_30_prediction.png")    
    historical_df = data.iloc[-70:][['close']]
    future_df = pd.DataFrame({'close': predicted_prices}, index=future_timestamps)

    full_df = pd.concat([historical_df, future_df])

    plt.figure(figsize=(12, 6))
    plt.plot(full_df.index, full_df["close"], color="blue", linestyle="-", marker="o", label="Historical & Predicted Prices")
    plt.plot(future_df.index, future_df["close"], color="red", linestyle="-", marker="o", label="Predicted Prices (10, 20, 30 min)", zorder=3)
    plt.annotate(f"${predicted_prices[-1]:.2f}", (future_df.index[-1], predicted_prices[-1]), fontsize=10, color="red")

    plt.xlabel("Timestamp (UTC)")
    plt.ylabel("Close Price (USDT)")
    plt.title(f"{symbol}- Historical & Future Predictions (Last 70% Actual + Next 30% Predicted)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    plt.savefig(graph_path)
    plt.close()