# myproject/celery.py
# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Trading.settings')  # change `myproject`

# app = Celery('Trading')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.update(
#     task_pool='solo'
# )
# app.autodiscover_tasks()

# crypticron_trade/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set default Django settings module for 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Trading.settings')

app = Celery('Trading')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Ensure the task is loaded
app.autodiscover_tasks(lambda: ['crypticron_trade.tasks'])