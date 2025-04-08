# import json
# import asyncio
# import websockets
# from urllib.parse import parse_qs
# from channels.generic.websocket import AsyncWebsocketConsumer

# BINANCE_WS_BASE_URL = "wss://stream.binance.com:9443/ws"

# class AllBinanceConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Get the query parameter from the WebSocket URL
#         query_params = parse_qs(self.scope["query_string"].decode())
#         self.symbols = query_params.get("symbol", ["BTCUSDT"])[0].upper().split(",")  # Default to BTCUSDT if not provided

#         # Construct the WebSocket URL for Binance
#         self.binance_ws_url = f"{BINANCE_WS_BASE_URL}/{'/'.join([s.lower() + '@kline_1m' for s in self.symbols])}"

#         await self.accept()
#         self.loop = asyncio.get_event_loop()
#         self.task = self.loop.create_task(self.fetch_binance_data())

#     async def disconnect(self, close_code):
#         if hasattr(self, "task"):
#             self.task.cancel()

#     async def receive(self, text_data):
#         pass  # No incoming messages are needed

#     async def fetch_binance_data(self):
#         async with websockets.connect(self.binance_ws_url) as ws:
#             while True:
#                 data = await ws.recv()
#                 json_data = json.loads(data)

#                 kline = json_data["k"]
#                 payload = {
#                     "symbol": json_data["s"],
#                     "timestamp": kline["t"],
#                     "open": kline["o"],
#                     "high": kline["h"],
#                     "low": kline["l"],
#                     "close": kline["c"],
#                     "volume": kline["v"],
#                 }

#                 await self.send(text_data=json.dumps(payload))



# import json
# import asyncio
# import websockets
# import requests
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.conf import settings

# BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/!ticker@arr"
# COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

# API_KEY = settings.API_KEY
# HEADERS_CMC = {"X-CMC_PRO_API_KEY": settings.COIN_MARKET_KEY}


# class AllBinanceConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         self.market_cap_data = {}

#         # Start WebSocket data fetching
#         self.binance_task = asyncio.create_task(self.fetch_binance_data())
#         self.market_cap_task = asyncio.create_task(self.fetch_market_cap_data())

#     async def disconnect(self, close_code):
#         if self.binance_task:
#             self.binance_task.cancel()
#         if self.market_cap_task:
#             self.market_cap_task.cancel()

#     async def fetch_binance_data(self):
#         async with websockets.connect(BINANCE_WS_URL) as websocket:
#             while True:
#                 data = await websocket.recv()
#                 parsed_data = json.loads(data)
#                 symbols_data = []
                
#                 for item in parsed_data:
#                     symbol = item['s']
#                     if symbol.endswith("USDT"):  # Filter only USDT pairs
#                         try:
#                             price = float(item['c'])
#                             open_24h = float(item['o'])  # 24h Open Price
#                             open_1h = float(item.get("h1", open_24h))  # Approx 1h Open
#                             open_4h = float(item.get("h4", open_24h))  # Approx 4h Open

#                             change_24h = ((price - open_24h) / open_24h) * 100
#                             change_1h = ((price - open_1h) / open_1h) * 100
#                             change_4h = ((price - open_4h) / open_4h) * 100

#                             formatted_entry = {
#                                 "symbol": symbol,
#                                 "name": symbol[:-4],  # Extracting coin name from symbol
#                                 "price": f"${price:,.2f}",
#                                 "24h_change": f"{change_24h:+.2f}%",
#                                 "4h_change": f"{change_4h:+.2f}%",
#                                 "1h_change": f"{change_1h:+.2f}%",
#                                 "24h_volume": f"${float(item['v']):,.2f}B",
#                                 "market_cap": self.market_cap_data.get(symbol[:-4], "N/A")
#                             }
#                             symbols_data.append(formatted_entry)
#                         except Exception as e:
#                             print(f"Error processing {symbol}: {e}")

#                 await self.send(json.dumps({"symbols": symbols_data}))
#                 await asyncio.sleep(1)

#     async def fetch_market_cap_data(self):
#         while True:
#             try:
#                 response = requests.get(COINMARKETCAP_URL, headers=HEADERS_CMC)
#                 if response.status_code == 200:
#                     data = response.json().get("data", [])
#                     self.market_cap_data = {item['symbol']: f"${item['quote']['USD']['market_cap']:,.2f}B" for item in data}
#                 await asyncio.sleep(60)  # Fetch market cap every minute
#             except Exception as e:
#                 print(f"Error fetching market cap data: {e}")
#                 await asyncio.sleep(10)


# import json
# import asyncio
# import websockets
# import requests
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.conf import settings
# from collections import deque
# BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/!ticker@arr"
# COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

# API_KEY = settings.API_KEY
# HEADERS_CMC = {"X-CMC_PRO_API_KEY": settings.COIN_MARKET_KEY}


# class AllBinanceConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         self.market_cap_data = {}
# # Store price history for sparklines (24-hour data with max 1440 entries for 1-min updates)
#         self.price_history = {}  # Format: {"BTCUSDT": deque([87314.1, 87300.5, ...])}

#         # Start WebSocket data fetching
#         self.binance_task = asyncio.create_task(self.fetch_binance_data())
#         self.market_cap_task = asyncio.create_task(self.fetch_market_cap_data())
#         self.sparkline_task = asyncio.create_task(self.fetch_sparkline_data())
        
#     async def disconnect(self, close_code):
#         if self.binance_task:
#             self.binance_task.cancel()
#         if self.market_cap_task:
#             self.market_cap_task.cancel()
#         if self.sparkline_task:
#             self.sparkline_task.cancel()
#     async def fetch_binance_data(self):
#         async with websockets.connect(BINANCE_WS_URL) as websocket:
#             while True:
#                 data = await websocket.recv()
#                 parsed_data = json.loads(data)
#                 symbols_data = []
                
#                 for item in parsed_data:
#                     symbol = item['s']
#                     if symbol.endswith("USDT"):  # Filter only USDT pairs                    
#                         try:
#                             price = float(item['c'])
                            
#                             # **Update price history for sparklines**
#                             # if symbol not in self.price_history:
#                             #     self.price_history[symbol] = deque(maxlen=1440)  # 1-min updates, 24 hours
#                             # self.price_history[symbol].append(price)  # Append latest price
#                             open_24h = float(item['o'])  # 24h Open Price
#                             open_1h = float(item.get("h1", open_24h))  # Approx 1h Open
#                             open_4h = float(item.get("h4", open_24h))  # Approx 4h Open

#                             change_24h = ((price - open_24h) / open_24h) * 100
#                             change_1h = ((price - open_1h) / open_1h) * 100
#                             change_4h = ((price - open_4h) / open_4h) * 100

#                             formatted_entry = {
#                                 "symbol": symbol,
#                                 "name": symbol[:-4],  # Extracting coin name from symbol
#                                 "price": f"${price:,.2f}",
#                                 "24h_change": f"{change_24h:+.2f}%",
#                                 "4h_change": f"{change_4h:+.2f}%",
#                                 "1h_change": f"{change_1h:+.2f}%",
#                                 "24h_volume": f"${float(item['v']):,.2f}B",
#                                 "market_cap": self.market_cap_data.get(symbol[:-4], "N/A"),
#                                 # "sparkline": list(self.price_history[symbol])  # Send price history
#                                 "sparkline": list(self.price_history.get(symbol, []))  # Retrieve stored sparkline
#                             }
#                             symbols_data.append(formatted_entry)
#                         except Exception as e:
#                             print(f"Error processing {symbol}: {e}")

#                 await self.send(json.dumps({"symbols": symbols_data}))
#                 await asyncio.sleep(1)

#     async def fetch_market_cap_data(self):
#         while True:
#             try:
#                 response = requests.get(COINMARKETCAP_URL, headers=HEADERS_CMC)
#                 if response.status_code == 200:
#                     data = response.json().get("data", [])
#                     self.market_cap_data = {item['symbol']: f"${item['quote']['USD']['market_cap']:,.2f}B" for item in data}
#                 await asyncio.sleep(60)  # Fetch market cap every minute
#             except Exception as e:
#                 print(f"Error fetching market cap data: {e}")
#                 await asyncio.sleep(10)
#     # async def cleanup_old_sparkline_data(self):
#     #     """Updates the price history every minute."""
#     #     while True:
#     #         await asyncio.sleep(60)  # Store data every 1 minute   86400
            
#     #         for symbol, prices in self.price_history.items():
#     #             if len(prices) > 0:
#     #                 last_price = prices[-1]  # Get the latest price
#     #                 self.price_history[symbol].append(last_price)  # Store for sparkline

#     async def fetch_sparkline_data(self):
#         """Continuously updates price history for sparklines in the background."""
#         async with websockets.connect(BINANCE_WS_URL) as websocket:
#             while True:
#                 data = await websocket.recv()
#                 parsed_data = json.loads(data)

#                 for item in parsed_data:
#                     symbol = item['s']
#                     if symbol.endswith("USDT"):  # Only USDT pairs
#                         try:
#                             price = float(item['c'])
#                             if symbol not in self.price_history:
#                                 self.price_history[symbol] = deque(maxlen=1440)  # Store last 24 hours (1-min updates)
#                             self.price_history[symbol].append(price)  # Append the latest price
#                         except Exception as e:
#                             print(f"Error updating sparkline for {symbol}: {e}")

#                 await asyncio.sleep(60)  # Update sparkline data every 1 minute


import json
import asyncio
import websockets
import requests
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/!ticker@arr"
COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

API_KEY = settings.API_KEY
HEADERS_CMC = {"X-CMC_PRO_API_KEY": settings.COIN_MARKET_KEY}


class AllBinanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.market_cap_data = {}
        self.sparkline_data = {}  # Store sparkline price data
        self.last_sparkline_update = datetime.utcnow()

        # Start WebSocket data fetching
        self.binance_task = asyncio.create_task(self.fetch_binance_data())
        self.market_cap_task = asyncio.create_task(self.fetch_market_cap_data())

    async def disconnect(self, close_code):
        if self.binance_task:
            self.binance_task.cancel()
        if self.market_cap_task:
            self.market_cap_task.cancel()

    async def fetch_binance_data(self):
        async with websockets.connect(BINANCE_WS_URL) as websocket:
            while True:
                data = await websocket.recv()
                parsed_data = json.loads(data)
                symbols_data = []

                for item in parsed_data:
                    symbol = item['s']
                    if symbol.endswith("USDT"):  # Filter only USDT pairs
                        try:
                            price = float(item['c'])
                            open_24h = float(item['o'])  # 24h Open Price
                            open_1h = float(item.get("h1", open_24h))  # Approx 1h Open
                            open_4h = float(item.get("h4", open_24h))  # Approx 4h Open

                            change_24h = ((price - open_24h) / open_24h) * 100
                            change_1h = ((price - open_1h) / open_1h) * 100
                            change_4h = ((price - open_4h) / open_4h) * 100

                            # Update sparkline data separately
                            self.update_sparkline_data(symbol, price)

                            formatted_entry = {
                                "symbol": symbol,
                                "name": symbol[:-4],  # Extracting coin name from symbol
                                "price": f"${price:,.2f}",
                                "24h_change": f"{change_24h:+.2f}%",
                                "4h_change": f"{change_4h:+.2f}%",
                                "1h_change": f"{change_1h:+.2f}%",
                                "24h_volume": f"${float(item['v']):,.2f}B",
                                "market_cap": self.market_cap_data.get(symbol[:-4], "N/A"),
                                "sparkline": self.sparkline_data.get(symbol, [])
                            }
                            symbols_data.append(formatted_entry)
                        except Exception as e:
                            print(f"Error processing {symbol}: {e}")

                await self.send(json.dumps({"symbols": symbols_data}))
                await asyncio.sleep(1)

    async def fetch_market_cap_data(self):
        while True:
            try:
                response = requests.get(COINMARKETCAP_URL, headers=HEADERS_CMC)
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    self.market_cap_data = {
                        item['symbol']: f"${item['quote']['USD']['market_cap']:,.2f}B"
                        for item in data
                    }
                await asyncio.sleep(60)  # Fetch market cap every minute
            except Exception as e:
                print(f"Error fetching market cap data: {e}")
                await asyncio.sleep(10)

    def update_sparkline_data(self, symbol, price):
        """Updates the sparkline data every 24 hours and keeps the last 7 entries."""
        now = datetime.utcnow()
        if symbol not in self.sparkline_data:
            self.sparkline_data[symbol] = []  # Initialize if not present

        if (now - self.last_sparkline_update) >= timedelta(hours=24):
            if len(self.sparkline_data[symbol]) >= 7:  # Keep last 7 days
                self.sparkline_data[symbol].pop(0)
            self.sparkline_data[symbol].append(price)
        
        # Reset last update timestamp once per day
        self.last_sparkline_update = now
