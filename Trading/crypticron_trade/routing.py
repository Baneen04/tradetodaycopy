# from django.urls import re_path
# from .consumers import BTCChartConsumer

# websocket_urlpatterns = [
#     re_path(r"ws/binance-data/$", BTCChartConsumer.as_asgi()),
# ]

from django.urls import re_path
from crypticron_trade.consumers.live_btc_consumer import BinanceConsumer
from crypticron_trade.consumers.symbol_data import AllBinanceConsumer
from crypticron_trade.consumers.test import BTCConsumer
from crypticron_trade.consumers.live import BinanceConsumer_live
from crypticron_trade.consumers.updating import BinanceConsumer_data

websocket_urlpatterns = [
    re_path(r'ws/binance/$', BinanceConsumer.as_asgi()),
    re_path(r'ws/binance-data/$', AllBinanceConsumer.as_asgi()) , # Ensuring exact match
    # re_path(r"ws/kline/(?P<symbol>\w+)/$", KlineConsumer.as_asgi()),
    re_path(r'ws/btc_chart/$', BTCConsumer.as_asgi()),
    re_path(r'ws/live/$',BinanceConsumer_live.as_asgi()),
    re_path(r'ws/update/$',BinanceConsumer_data.as_asgi()),
]


