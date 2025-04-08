import jax
import jax.numpy as jnp
import optax
import numpy as np
import pandas as pd
import ccxt
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from django.conf import settings
import os

# Fetch historical BTC data from Binance (15-minute intervals)
def fetch_binance_data(symbol='BTCUSDT', timeframe='15m', limit=1000):
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return None

# Prepare data for the model
def prepare_data(df, lookback=96):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[['close']])

    X, y = [], []
    for i in range(lookback, len(scaled_data) - 3):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i:i+4, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], lookback, 1))
    return jnp.array(X), jnp.array(y), scaler

# Define a simple MLP model
def create_model(params, x):
    x = x.reshape(x.shape[0], -1)
    for w, b in params[:-1]:
        x = jax.nn.relu(jnp.dot(x, w) + b)
    w, b = params[-1]
    return jnp.dot(x, w) + b

# Initialize model parameters
def init_params(layer_sizes, key):
    keys = jax.random.split(key, len(layer_sizes))
    params = []
    for i, (in_size, out_size) in enumerate(zip(layer_sizes[:-1], layer_sizes[1:])):
        w = jax.random.normal(keys[i], (in_size, out_size)) * 0.01
        b = jnp.zeros(out_size)
        params.append((w, b))
    return params

# Loss function
def loss_fn(params, x, y):
    preds = create_model(params, x)
    return jnp.mean((preds - y) ** 2)

# Optimizer
optimizer = optax.adam(learning_rate=0.001)

# Training step
@jax.jit
def train_step(params, opt_state, x, y):
    loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
    updates, opt_state = optimizer.update(grads, opt_state, params)
    params = optax.apply_updates(params, updates)
    return params, opt_state, loss

def predict_btc_1h():
    data = fetch_binance_data(timeframe='15m', limit=1000)
    if data is None:
        return {"error": "Failed to fetch data from Binance."}

    lookback = 96
    X, y, scaler = prepare_data(data, lookback)
    
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    key = jax.random.PRNGKey(0)
    layer_sizes = [lookback, 64, 32, 4]
    params = init_params(layer_sizes, key)
    
    opt_state = optimizer.init(params)
    
    epochs = 10
    batch_size = 32
    for epoch in range(epochs):
        for i in range(0, len(X_train), batch_size):
            X_batch = X_train[i:i + batch_size]
            y_batch = y_train[i:i + batch_size]
            params, opt_state, loss = train_step(params, opt_state, X_batch, y_batch)
    
    # Generate Predictions
    last_sequence = X[-1].reshape(1, lookback, 1)
    predicted_scaled = create_model(params, last_sequence)
    predicted_prices = scaler.inverse_transform(predicted_scaled.reshape(1, -1))[0]
    
    # Calculate confidence interval
    std_dev = np.std(predicted_prices)
    confidence_percentage = 100 - (std_dev / np.mean(predicted_prices)) * 100
    lower_bound = predicted_prices - std_dev
    upper_bound = predicted_prices + std_dev
    
    last_timestamp = data.index[-1]
    next_timestamps = [last_timestamp + timedelta(minutes=15 * i) for i in range(1, 5)]
    
    # Save Prediction Graph
    graph_path = os.path.join(settings.MEDIA_ROOT, "hour1_prediction.png")
    plt.figure(figsize=(12, 6))
    last_actual_price = data["close"].iloc[-1]
    full_timestamps = [last_timestamp] + next_timestamps
    full_prices = [last_actual_price] + list(predicted_prices)
    
    plt.plot(data.index[-10:], data["close"].iloc[-10:], color="blue", linestyle="-", marker="o", label="Historical Prices")
    plt.plot(full_timestamps, full_prices, color="red", linestyle="-", marker="o", label="Predicted Prices")
    plt.fill_between(next_timestamps, lower_bound, upper_bound, color='red', alpha=0.2, label="Confidence Interval")
    
    # Label last predicted value
    plt.annotate(f"{predicted_prices[-1]:.2f}", (next_timestamps[-1], predicted_prices[-1]), fontsize=10, color="red")
    
    plt.xlabel("Timestamp (UTC)")
    plt.ylabel("Close Price (USDT)")
    plt.title("BTCUSDT - Predictions for Next Hour (15m Intervals) with Confidence Intervals")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()
    
    return {
        "predictions": [
        {
            "timestamp": str(ts),
            "predicted_price": f"${float(predicted_prices[i]):,.2f}",
            "confidence": f"{float(confidence_percentage):.2f}%",
            "range": f"${float(lower_bound[i]):,.2f} - ${float(upper_bound[i]):,.2f}"
        }
        for i, ts in enumerate(next_timestamps)
    ],
    "graph_url": "media/hour1_prediction.png"
}
    