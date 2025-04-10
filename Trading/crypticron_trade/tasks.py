# from celery import shared_task

# @shared_task
# def update_binance_data_task():
#     from crypticron_trade.utils.min_15m_db import store_prediction
#     store_prediction("BTCUSDT")
from celery import shared_task

@shared_task
def update_binance_data_task(symbol):
    print(f"Running scheduled prediction for: {symbol}")
    from crypticron_trade.utils.min_15m_db import store_prediction
    store_prediction("BTCUSDT")
