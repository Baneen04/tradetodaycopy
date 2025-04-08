import json
import time
import requests
import numpy as np
import pandas as pd
import asyncio
from datetime import datetime, timedelta, timezone
from channels.generic.websocket import AsyncWebsocketConsumer

BINANCE_URL = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=60"

class BTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        while True:
            data = await self.fetch_live_data()
            await self.send(json.dumps(data))
            await asyncio.sleep(60)  # Update every minute

    async def fetch_live_data(self):
        response = requests.get(BINANCE_URL)
        data = response.json()

        timestamps = [datetime.utcfromtimestamp(entry[0] / 1000).replace(tzinfo=timezone.utc).isoformat() for entry in data]
        close_prices = [float(entry[4]) for entry in data]

        future_time, predicted_prices = self.predict_prices(close_prices[-1], timestamps[-1])

        return {
            "timestamps": timestamps,
            "close_prices": close_prices,
            "future_time": future_time,
            "predicted_prices": predicted_prices,
        }

    def predict_prices(self, last_price, last_time):
        future_time = [(datetime.fromisoformat(last_time) + timedelta(minutes=i)).isoformat() for i in range(0, 61, 15)]
        predicted_prices = [last_price] + list(last_price + np.cumsum(np.random.uniform(-50, 50, size=4)))

        return future_time, predicted_prices
