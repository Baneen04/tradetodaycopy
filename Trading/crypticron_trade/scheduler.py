# crypticron_trade/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from crypticron_trade.utils.min_15m_db import predict_15crypto

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(predict_15crypto, 'interval', minutes=15)
    scheduler.start()
