import json
import asyncio
import websockets
import aiohttp
import time
from urllib.parse import parse_qs
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer

BINANCE_WS_BASE_URL = "wss://stream.binance.com:9443/ws"
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"
MAX_CANDLES_PER_REQUEST = 1000  # Binance allows max 1000 candles per request

# Define timeframes
TIMEFRAMES = ["1m", "15m", "30m", "1h", "1d"]

class BinanceConsumer_data(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        self.symbols = query_params.get("symbol", ["BTCUSDT"])[0].upper().split(",")
        self.timeframes = query_params.get("timeframes", ["1m,15m,30m,1h,1d"])[0].split(",")
        self.timeframes = [tf for tf in self.timeframes if tf in TIMEFRAMES]
        
        if "1m" in self.timeframes:
            self.binance_ws_url = f"{BINANCE_WS_BASE_URL}/{'/'.join([s.lower() + '@kline_1m' for s in self.symbols])}"
        else:
            self.binance_ws_url = None
        
        await self.accept()
        await self.send_historical_data()
        
        if self.binance_ws_url:
            self.loop = asyncio.get_event_loop()
            self.task = self.loop.create_task(self.fetch_binance_data())

    async def disconnect(self, close_code):
        if hasattr(self, "task"):
            self.task.cancel()

    async def receive(self, text_data):
        pass  # No incoming messages are needed

    async def send_historical_data(self):
        """Fetch and send the last 1 month of historical Kline data for all timeframes."""
        async with aiohttp.ClientSession() as session:
            for symbol in self.symbols:
                historical_data = {}
                for timeframe in self.timeframes:
                    historical_data[timeframe] = await self.fetch_full_month_data(session, symbol, timeframe)
                await self.send(text_data=json.dumps({"symbol": symbol, "historical_data": historical_data}))

    async def fetch_full_month_data(self, session, symbol, interval):
        """Fetch the last 1 month of data for a given timeframe."""
        now = int(time.time() * 1000)
        one_month_ago = now - (30 * 24 * 60 * 60 * 1000)
        all_data = []
        start_time = one_month_ago

        while start_time < now:
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": MAX_CANDLES_PER_REQUEST,
                "startTime": start_time,
                "endTime": now,
            }
            async with session.get(BINANCE_API_URL, params=params) as response:
                if response.status == 200:
                    klines = await response.json()
                    if not klines:
                        break
                    
                    all_data.extend([
                        {
                            "timestamp": k[0],
                            "date": datetime.utcfromtimestamp(k[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                            "open": k[1],
                            "high": k[2],
                            "low": k[3],
                            "close": k[4],
                            "volume": k[5],
                        }
                        for k in klines
                    ])
                    start_time = klines[-1][0] + 60000  # Move start time forward
                else:
                    print(f"Failed to fetch data for {symbol} ({interval}): {response.status}")
                    break
        return all_data

    async def fetch_binance_data(self):
        """Stream real-time 1-minute data from Binance WebSocket."""
        async with websockets.connect(self.binance_ws_url) as ws:
            while True:
                try:
                    data = await ws.recv()
                    json_data = json.loads(data)
                    kline = json_data["k"]
                    timestamp = kline["t"]
                    payload = {
                        "symbol": json_data["s"],
                        "timeframe": "1s",
                        "timestamp": timestamp,
                        "date": datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                        "open": kline["o"],
                        "high": kline["h"],
                        "low": kline["l"],
                        "close": kline["c"],
                        "volume": kline["v"],
                    }
                    await self.send(text_data=json.dumps(payload))
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    break

# import json
# import asyncio
# import websockets
# import aiohttp
# import time
# import logging
# from urllib.parse import parse_qs
# from datetime import datetime
# from channels.generic.websocket import AsyncWebsocketConsumer

# BINANCE_WS_BASE_URL = "wss://stream.binance.com:9443/ws"
# BINANCE_API_URL = "https://api.binance.com/api/v3/klines"
# MAX_CANDLES_PER_REQUEST = 1000

# TIMEFRAMES = {"1m": "1m", "15m": "15m", "30m": "30m", "1h": "1h", "1d": "1d"}
# logging.basicConfig(level=logging.INFO)

# class BinanceConsumer_data(AsyncWebsocketConsumer):
#     async def connect(self):
#         query_params = parse_qs(self.scope["query_string"].decode())
#         self.symbol = query_params.get("symbol", ["BTCUSDT"])[0].upper()
#         self.timeframe = query_params.get("timeframe", ["1m"])[0]

#         self.binance_ws_url = f"{BINANCE_WS_BASE_URL}/{self.symbol.lower()}@kline_{self.timeframe}"
        
#         await self.accept()
#         logging.info(f"✅ Connected WebSocket for {self.symbol} ({self.timeframe})")
        
#         # Send historical data before streaming
#         await self.send_historical_data()

#         # Start WebSocket connection to Binance
#         asyncio.create_task(self.fetch_binance_data())

#     async def disconnect(self, close_code):
#         logging.info("❌ WebSocket disconnected")

#     async def send_historical_data(self):
#         async with aiohttp.ClientSession() as session:
#             params = {
#                 "symbol": self.symbol.upper(),
#                 "interval": self.timeframe,
#                 "limit": 50  # Fetch last 50 candles
#             }
#             async with session.get(BINANCE_API_URL, params=params) as response:
#                 if response.status == 200:
#                     klines = await response.json()
#                     candles = [{"timestamp": k[0], "open": k[1], "high": k[2], "low": k[3], "close": k[4]} for k in klines]
#                     await self.send(text_data=json.dumps({"historical": candles}))
#                     logging.info(f"📊 Sent historical data ({len(candles)} candles)")
#                 else:
#                     logging.error(f"Failed to fetch historical data: {response.status}")

#     async def fetch_binance_data(self):
#         try:
#             async with websockets.connect(self.binance_ws_url) as ws:
#                 async for message in ws:
#                     data = json.loads(message)
#                     if "data" in data and "k" in data["data"]:
#                         kline = data["data"]["k"]
#                         payload = {
#                             "timestamp": kline["t"],
#                             "open": kline["o"],
#                             "high": kline["h"],
#                             "low": kline["l"],
#                             "close": kline["c"]
#                         }
#                         await self.send(text_data=json.dumps(payload))
#         except Exception as e:
#             logging.error(f"WebSocket error: {e}")
#             await asyncio.sleep(5)  # Retry after 5 seconds
