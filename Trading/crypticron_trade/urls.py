from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import (
    min15_prediction_view, 
    min15_linegraph_view, 
    min30_prediction_view, 
    min30_linegraph_view,
    hour1_prediction_view,
    hour1_linegraph_view,
    # min_prediction_view,
    # min_linegraph_view,
    # btc_chart_view,
    # btc_prediction_view,
    binance_symbols_view,
    binance_symbols_interval_view,
    symbol15_prediction_view,
    symbol15_linegraph_view,
    symbol30_prediction_view,
    symbol30_linegraph_view,
    symbol1h_prediction_view,
    symbol1h_linegraph_view,
    SLTP_15view,
    SLTP_30view,
    SLTP_1hview,
    min15_prediction,
    min30_prediction,
    h1_prediction,
    kline_chart,
    fear_greed_chart_view,
    market_prediction_index_view,
    btc_chart_view,
    candlestick_chart,
    update_chart,
    fg_index_view,
    market_index,


    ## accuracy 
    prediction_acc,
    prediction_30acc,
    prediction_1hacc,
    h24_prediction,
    get_sparkline_data,
    get_multiple_sparklines,

    latest_prediction,
    start_prediction,
)    

urlpatterns = [
    ##for token 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ##15-min prediction
    path('predict/', min15_prediction_view, name='min15_prediction'),
    # path('graph/15min/', min15_linegraph_view, name='min15_linegraph'),
    # # path('15min-kline-graph/', min15_kline_view, name='min15_linegraph'),

    # ##30-min Prediction
    # path('predict/30min/', min30_prediction_view, name='min30_prediction'),
    # path('graph/30min/', min30_linegraph_view, name='min30_graph'),

    # ##hour 1 prediction
    # path('predict/hour1/', hour1_prediction_view, name='hour1_prediction'),
    # path('graph/hour1/', hour1_linegraph_view, name='hour1_graph'),

    ##test

     ##30-min Prediction
    # path('predict/min/', min_prediction_view, name='min30_prediction'),
    # path('graph/', btc_chart_view, name='min30_graph'),
    
    ##Binance All Symbol Data
    path('binance-all-symbols/', binance_symbols_view, name='binance_all_symbols'),
    path('binance-symbols-int/', binance_symbols_interval_view, name='binance_all_symbols_interval'),
    ##15 min for all SYMBOL
    path("predict/15/", symbol15_prediction_view, name="allcrypto_15min_prediction"),
    path("graph/15/", symbol15_linegraph_view, name="allcrypto_15min_graph"),
    ##30 min for all SYMBOL
    path("predict/30/", symbol30_prediction_view, name="allcrypto_30min_prediction"),
    path("graph/30/", symbol30_linegraph_view, name="allcrypto_30miin_graph"),
    ## 1h for all SYMBOL
    path("predict/1h/", symbol1h_prediction_view, name="allcrypto_1h_prediction"),
    path("graph/1h/", symbol1h_linegraph_view, name="allcrypto_1h_graph"),
    # path("predict/", predict_crypto_SLTPview, name="predict_crypto"),
    path('candlestick/', candlestick_chart, name='candlestick_chart'),
    path('update/', update_chart, name='candlestick_chart'),


#### accuracy testing
    path('acc-15min/', prediction_acc, name='15 min accuracy'),
    path('acc-30min/', prediction_30acc, name='30 min accuracy'),
    path('acc-1h/', prediction_1hacc, name='1 hour accuracy'),


    # correct prediction api
    path('predict/15min/', min15_prediction, name='15min_live_prediction'),
    path('predict/30min/', min30_prediction, name='30min_live_prediction'),
    path("predict/1hour/", h1_prediction, name="btc-predictions"),
    path("predict/24hour/", h24_prediction, name="24 hour predictions"),
    # path("kline-chart/", kline_chart, name="kline_chart"),

    #SL-TP API
    path('sl-tp15/',SLTP_15view,name='SL-TP 15 min Prediction'),
    path('sl-tp30/',SLTP_30view, name='SL-TP 30 min Prediction' ),
    path('sl-tp1h/',SLTP_1hview, name='SL-TP 1 hour Prediction' ),

    # FEAR GREED CHART 
    path('fear-greed/chart/', fear_greed_chart_view, name='fear_greed_chart'),
    path('fg-chart/', fg_index_view, name='fear_greed_chart'),

    ##Market Index
    path('market-index/', market_prediction_index_view, name='market_index'),
    path('mi/', market_index,name='market_index' ),

    #test- chart of 15 min prediction
    path('btc/', btc_chart_view),

    path('sparkline/', get_sparkline_data, name='sparkline'),
    path('sparklines/', get_multiple_sparklines, name='multiple_sparklines'),

    path('15min/', latest_prediction, name='15min_live_prediction'),
    path('start-prediction/', start_prediction, name='start_prediction'),
]


