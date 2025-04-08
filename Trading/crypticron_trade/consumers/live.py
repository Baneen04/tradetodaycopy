import json
import asyncio
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

class BinanceConsumer_live(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.is_connected = True  # Track connection status
        self.binance_task = asyncio.create_task(self.fetch_binance_ws_data())  # Start Binance WebSocket

    async def fetch_binance_ws_data(self):
        """Connects to Binance WebSocket and streams real-time BTCUSDT 1-minute candlestick data."""
        try:
            async with websockets.connect(BINANCE_WS_URL) as websocket:
                while self.is_connected:
                    response = await websocket.recv()
                    data = json.loads(response)

                    # Extract relevant OHLC data
                    kline = data.get("k", {})
                    candle_data = {
                        "time": kline.get("t"),  # Timestamp
                        "open": kline.get("o"),
                        "high": kline.get("h"),
                        "low": kline.get("l"),
                        "close": kline.get("c"),
                        "volume": kline.get("v")
                    }
                    print(f"Sending Data: {candle_data}")  # Debugging

                    # Send data to the WebSocket client
                    await self.send(text_data=json.dumps(candle_data))

        except asyncio.CancelledError:
            print("Binance WebSocket Task Cancelled.")
        except Exception as e:
            print(f"Binance WebSocket Error: {e}")

    async def disconnect(self, close_code):
        self.is_connected = False  # Stop streaming
        self.binance_task.cancel()  # Cancel the WebSocket task
        print(f"WebSocket Disconnected: {close_code}")
