from django.apps import AppConfig


class CrypticronTradeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crypticron_trade'
    
    def ready(self):
        from . import scheduler
        scheduler.start()


