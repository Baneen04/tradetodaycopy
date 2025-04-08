# from django.apps import AppConfig


# class AccountsConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'accounts'
# apps.py in your Django app
from django.apps import AppConfig
from mongoengine import connect, disconnect

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Disconnect existing MongoDB connection to avoid conflicts
        disconnect(alias='default')

        # Establish the MongoDB connection
        connect(
            db='trade_today',
            host='localhost',
            port=27017,
            alias='default'
        )
