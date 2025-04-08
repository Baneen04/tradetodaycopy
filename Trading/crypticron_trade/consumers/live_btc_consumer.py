# import json
# import asyncio
# import websockets
# import aiohttp
# import time
# from urllib.parse import parse_qs
# from datetime import datetime
# from channels.generic.websocket import AsyncWebsocketConsumer

# BINANCE_WS_BASE_URL = "wss://stream.binance.com:9443/ws"
# BINANCE_API_URL = "https://api.binance.com/api/v3/klines"
# MAX_CANDLES_PER_REQUEST = 1000  # Binance allows max 1000 candles per request

# # Define timeframes
# TIMEFRAMES = {
#     "1m": "1 minute",
#     "15m": "15 minutes",
#     "30m": "30 minutes",
#     "1h": "1 hour",
#     "1d": "1 day",
# }

# class BinanceConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         query_params = parse_qs(self.scope["query_string"].decode())
#         self.symbols = query_params.get("symbol", ["BTCUSDT"])[0].upper().split(",")
#         self.timeframes = query_params.get("timeframes", ["1m,15m,30m,1h,1d"])[0].split(",")

#         self.binance_ws_url = f"{BINANCE_WS_BASE_URL}/{'/'.join([s.lower() + '@kline_1m' for s in self.symbols])}"

#         await self.accept()
#         await self.send_historical_data()  # Fetch and send last 1 month of data
#         self.loop = asyncio.get_event_loop()
#         self.task = self.loop.create_task(self.fetch_binance_data())

#     async def disconnect(self, close_code):
#         if hasattr(self, "task"):
#             self.task.cancel()

#     async def receive(self, text_data):
#         pass  # No incoming messages are needed

#     async def send_historical_data(self):
#         """Fetch and send the last 1 month of historical Kline data for all timeframes."""
#         async with aiohttp.ClientSession() as session:
#             for symbol in self.symbols:
#                 historical_data = {}
#                 for timeframe in self.timeframes:
#                     if timeframe in TIMEFRAMES:
#                         historical_data[timeframe] = await self.fetch_full_month_data(session, symbol, timeframe)

#                 await self.send(text_data=json.dumps({"symbol": symbol, "historical_data": historical_data}))

#     async def fetch_full_month_data(self, session, symbol, interval):
#         """Fetch the last 1 month of data for a given timeframe (e.g., 1m, 15m, 30m, 1h, 1d)."""
#         now = int(time.time() * 1000)  # Current timestamp in milliseconds
#         one_month_ago = now - (30 * 24 * 60 * 60 * 1000)  # 30 days ago
#         all_data = []
#         start_time = one_month_ago

#         while start_time < now:
#             params = {
#                 "symbol": symbol.upper(),
#                 "interval": interval,
#                 "limit": MAX_CANDLES_PER_REQUEST,
#                 "startTime": start_time,
#                 "endTime": now,
#             }
#             async with session.get(BINANCE_API_URL, params=params) as response:
#                 if response.status == 200:
#                     klines = await response.json()
#                     if not klines:
#                         break  # No more data

#                     all_data.extend([
#                         {
#                             "symbol": symbol,
#                             "timeframe": interval,
#                             "timestamp": k[0],
#                             "date": datetime.utcfromtimestamp(k[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
#                             "open": k[1],
#                             "high": k[2],
#                             "low": k[3],
#                             "close": k[4],
#                             "volume": k[5],
#                         }
#                         for k in klines
#                     ])
#                     start_time = klines[-1][0] + 60000  # Move start time forward

#                 else:
#                     print(f"Failed to fetch data for {symbol} ({interval}): {response.status}")
#                     break

#         return all_data

#     async def fetch_binance_data(self):
#         """Stream real-time 1-minute data from Binance WebSocket."""
#         async with websockets.connect(self.binance_ws_url) as ws:
#             while True:
#                 data = await ws.recv()
#                 json_data = json.loads(data)

#                 kline = json_data["k"]
#                 timestamp = kline["t"]
#                 payload = {
#                     "symbol": json_data["s"],
#                     "timeframe": "1m",
#                     "timestamp": timestamp,
#                     "date": datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S'),
#                     "open": kline["o"],
#                     "high": kline["h"],
#                     "low": kline["l"],
#                     "close": kline["c"],
#                     "volume": kline["v"],
#                 }

#                 await self.send(text_data=json.dumps(payload))

import json
import asyncio
import websockets
import aiohttp
import time
from urllib.parse import parse_qs
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer

BINANCE_WS_BASE_URL = "wss://stream.binance.com:9443/stream"
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"
MAX_CANDLES_PER_REQUEST = 1000  
TIMEFRAMES = ["1m", "15m", "30m", "1h", "1d"]

class BinanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Establish WebSocket connection and start streaming live data."""
        query_params = parse_qs(self.scope["query_string"].decode())

        self.symbols = query_params.get("symbol", ["BTCUSDT"])[0].upper().split(",")
        self.timeframes = query_params.get("timeframes", ["1m,15m,30m,1h,1d"])[0].split(",")
        self.timeframes = [tf for tf in self.timeframes if tf in TIMEFRAMES]

        streams = [f"{symbol.lower()}@kline_{tf}" for symbol in self.symbols for tf in self.timeframes]
        self.binance_ws_url = f"{BINANCE_WS_BASE_URL}?streams={'/'.join(streams)}"

        print(f"[CONNECTING] Connecting to Binance WebSocket: {self.binance_ws_url}")

        await self.accept()
        await self.send_historical_data()  
        self.loop = asyncio.get_event_loop()
        self.task = self.loop.create_task(self.fetch_binance_data())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, "task"):
            self.task.cancel()
        print(f"[DISCONNECTED] WebSocket closed with code: {close_code}")

    async def send_historical_data(self):
        """Fetch and send 1-month historical Kline data for all timeframes."""
        async with aiohttp.ClientSession() as session:
            for symbol in self.symbols:
                historical_data = {}
                for timeframe in self.timeframes:
                    print(f"[HISTORICAL] Fetching {symbol} {timeframe} data...")
                    historical_data[timeframe] = await self.fetch_full_month_data(session, symbol, timeframe)

                await self.send(text_data=json.dumps({"symbol": symbol, "historical_data": historical_data}))
                print(f"[HISTORICAL] Sent {symbol} historical data.")

    async def fetch_full_month_data(self, session, symbol, interval):
        """Fetch 1-month historical data for a given timeframe."""
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
                            "symbol": symbol,
                            "timeframe": interval,
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
                    start_time = klines[-1][0] + 60000  

                else:
                    print(f"[ERROR] Failed to fetch {symbol} ({interval}): {response.status}")
                    break

        return all_data

    async def fetch_binance_data(self):
        """Stream real-time Kline data from Binance WebSocket."""
        while True:
            try:
                async with websockets.connect(self.binance_ws_url) as ws:
                    print("[CONNECTED] Binance WebSocket streaming started.")
                    while True:
                        data = await ws.recv()
                        json_data = json.loads(data)

                        if "stream" in json_data and "data" in json_data:
                            kline_data = json_data["data"]["k"]
                            timestamp = kline_data["t"]
                            timeframe = json_data["stream"].split("@kline_")[1]
                            candle_closed = kline_data["x"]  

                            # Wait for the candle to fully close before sending data
                            if not candle_closed:
                                continue  

                            payload = {
                                "symbol": json_data["data"]["s"],
                                "timeframe": timeframe,
                                "timestamp": timestamp,
                                "date": datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                                "open": kline_data["o"],
                                "high": kline_data["h"],
                                "low": kline_data["l"],
                                "close": kline_data["c"],
                                "volume": kline_data["v"],
                            }

                            print(f"[LIVE] {payload}")  
                            await self.send(text_data=json.dumps(payload))

                            # Sleep for the corresponding timeframe
                            await self.wait_for_next_candle(timeframe)

            except websockets.exceptions.ConnectionClosed as e:
                print(f"[ERROR] WebSocket lost: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)  
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}. Restarting WebSocket...")
                await asyncio.sleep(5)

    async def wait_for_next_candle(self, timeframe):
        """Wait for the next candle to start based on timeframe."""
        time_intervals = {
            "1m": 60,  
            "15m": 900,  
            "30m": 1800,  
            "1h": 3600,  
            "1d": 86400  
        }
        if timeframe in time_intervals:
            await asyncio.sleep(time_intervals[timeframe])  

