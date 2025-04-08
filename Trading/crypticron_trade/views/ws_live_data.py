# from django.http import JsonResponse
# import json
# import asyncio
# import websockets

# BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
# latest_candle = {}

# async def fetch_latest_candle():
#     async with websockets.connect(BINANCE_WS_URL) as websocket:
#         global latest_candle
#         while True:
#             data = json.loads(await websocket.recv())
#             kline = data.get("k", {})
#             if kline:
#                 latest_candle = {
#                     "timestamp": kline["t"],
#                     "open": kline["o"],
#                     "high": kline["h"],
#                     "low": kline["l"],
#                     "close": kline["c"],
#                     "volume": kline["v"],
#                     "is_closed": kline["x"]
#                 }

# asyncio.create_task(fetch_latest_candle())  # Start fetching live data

# def latest_candle_view(request):
#     return JsonResponse(latest_candle if latest_candle else {"message": "No data yet"})


from django.shortcuts import render

def kline_chart(request):
    return render(request, "live_chart.html")  # Ensure you create this template
