from .min_15_views import min15_prediction_view, min15_linegraph_view
from .min_30_views import min30_prediction_view,min30_linegraph_view
from .hour1_view import hour1_prediction_view, hour1_linegraph_view
from .ws_live_data import kline_chart
from .binance_symbol_views import binance_symbols_view, binance_symbols_interval_view
from .symbol_15_views import symbol15_prediction_view, symbol15_linegraph_view
from .symbol_30_views import symbol30_prediction_view, symbol30_linegraph_view
from .symbol_1h_view import symbol1h_prediction_view, symbol1h_linegraph_view
from .test import candlestick_chart, update_chart
####COrrect    apiissss viewssssss
from .sl_tp_15views import SLTP_15view
from .sl_tp_30views import SLTP_30view
from .sl_tp_1hview import SLTP_1hview
from .symbol_15min_views import min15_prediction
from .symbol_30min_view import min30_prediction
from .symbol_1hview import h1_prediction
from .FG_index_views import fear_greed_chart_view, fg_index_view
from .market_view import market_prediction_index_view, market_index
from .min15_chart_pre import btc_chart_view
from .hour24_views import h24_prediction

##imporving accuracy
from .acc_symbol import prediction_acc, prediction_30acc, prediction_1hacc
from .sparkline_views import get_multiple_sparklines, get_sparkline_data

from .min15_db import symbol15_db_view, StorePredictionView, symbol30_db_view, Store30PredictionView, symbol1h_db_view, Store1hPredictionView

