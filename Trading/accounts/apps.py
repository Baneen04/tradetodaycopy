
# apps.py in your Django app
from django.apps import AppConfig
# from mongoengine import connect, disconnect

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
