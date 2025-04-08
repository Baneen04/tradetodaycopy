import os
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

# Fetch BTCUSDT data from Binance
def fetch_binance_data(symbol='BTCUSDT', timeframe='1m', limit=1000):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# Prepare data for model
def prepare_data(df, lookback=60):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df[['close']])

    X, y = [], []
    for i in range(lookback, len(scaled_data) - 30, 10):
        X.append(scaled_data[i - lookback:i, 0])
        y.append([scaled_data[i + 9, 0], scaled_data[i + 19, 0], scaled_data[i + 29, 0]])

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], lookback, 1))
    return jnp.array(X), jnp.array(y), scaler

# Define MLP model
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

optimizer = optax.adam(learning_rate=0.001)
# Training step
@jax.jit
def train_step(params, opt_state, x, y):
    loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
    updates, opt_state = optimizer.update(grads, opt_state, params)
    params = optax.apply_updates(params, updates)
    return params, opt_state, loss

def predict_btc_30():
    data = fetch_binance_data(timeframe='1m', limit=1000)
    lookback = 60
    X, y, scaler = prepare_data(data, lookback)

    # Train-test split
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Initialize model
    key = jax.random.PRNGKey(0)
    layer_sizes = [lookback, 64, 32, 3]
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
    last_sequence = X[-1].reshape(1, lookback, 1)
    predicted_scaled = create_model(params, last_sequence)
    predicted_prices = scaler.inverse_transform(predicted_scaled.reshape(1, -1))[0]

    # Convert to Python floats
    predicted_prices = [float(price) for price in predicted_prices]

    actual_prices = scaler.inverse_transform(y_test[:1].reshape(1, -1))[0]
    errors = np.abs(predicted_prices - actual_prices)
    mape = np.mean((errors / actual_prices) * 100)
    confidence_percent = max(100 - mape, 50)  # Ensuring a minimum confidence of 50%
    confidence_range = float(np.std(errors))  # Convert NumPy float to Python float

    last_timestamp = data.index[-1]
    future_timestamps = [last_timestamp + timedelta(minutes=i) for i in [10, 20, 30]]

    # Create a formatted response
    predictions = {
        "Predicted BTC Prices (with Confidence Intervals)": []
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
        predictions["Predicted BTC Prices (with Confidence Intervals)"].append(formatted_prediction)

    # Generate and save graph
    generate_graph(data, future_timestamps, predicted_prices)

    return predictions

# Path for saving the graph
graph_path= os.path.join(settings.MEDIA_ROOT, "30min_prediction.png")
# Graph Generation
def generate_graph(data, future_timestamps, predicted_prices):
    historical_df = data.iloc[-70:][['close']]
    future_df = pd.DataFrame({'close': predicted_prices}, index=future_timestamps)

    full_df = pd.concat([historical_df, future_df])

    plt.figure(figsize=(12, 6))
    plt.plot(full_df.index, full_df["close"], color="blue", linestyle="-", marker="o", label="Historical & Predicted Prices")
    plt.plot(future_df.index, future_df["close"], color="red", linestyle="-", marker="o", label="Predicted Prices (10, 20, 30 min)", zorder=3)
    plt.annotate(f"${predicted_prices[-1]:.2f}", (future_df.index[-1], predicted_prices[-1]), fontsize=10, color="red")

    plt.xlabel("Timestamp (UTC)")
    plt.ylabel("Close Price (USDT)")
    plt.title("BTCUSDT - Historical & Future Predictions (Last 70% Actual + Next 30% Predicted)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    plt.savefig(graph_path)
    plt.close()
