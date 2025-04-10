# from django.apps import AppConfig

# from django.db.models.signals import post_migrate
# from django.dispatch import receiver
# import logging

# import time
# # logger = logging.getLogger(__name__)

# class CrypticronTradeConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'crypticron_trade'

#     # time.sleep(120)
#     def ready(self):
#         # from django_celery_beat.models import PeriodicTask, IntervalSchedule
#         print("CrypticronTradeConfig is ready and post_migrate signal will be connected.")
#         # Connect the post_migrate signal after apps are ready
#         post_migrate.connect(create_periodic_task, sender=self)
#         print("Post-migrate signal connected.")
#     #     self.run_immediate_task()

#     # def run_immediate_task(self):
#     #     # This function will be used to run the task immediately upon server startup
#     #     from crypticron_trade.task import update_binance_data_task

#     #     update_binance_data_task.apply()  # Run the task immediately upon startup
#     #     print("Periodic task created successfully.")

# def create_periodic_task(sender, **kwargs):
#     print("Post-migrate signal received, checking for periodic task creation.")
#     from django_celery_beat.models import PeriodicTask, IntervalSchedule
#     # Check if the periodic task already exists
#     if not PeriodicTask.objects.filter(name="Update Binance BTCUSDT Prediction Every 15min").exists():
#         print("Periodic task doesn't exist, creating a new one.")

#         # Create schedule and periodic task
#         schedule, created = IntervalSchedule.objects.get_or_create(
#             every=15,
#             period=IntervalSchedule.MINUTES,
#         )
#         PeriodicTask.objects.create(
#             interval=schedule,
#             name='Update Binance BTCUSDT Prediction Every 15min',
#             task='crypticron_trade.tasks.update_binance_data_task',  # Replace with the correct task name
#         )
#         print("Periodic task created successfully.")
#     else:
#         print("Periodic task already exists.")


from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

import json

class CrypticronTradeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crypticron_trade'

    def ready(self):
        """This method will be called when the app is ready"""
        print("CrypticronTradeConfig is ready and post_migrate signal will be connected.")
        # Connect the post_migrate signal to your custom handler
        post_migrate.connect(self.create_periodic_task, sender=self)

    def create_periodic_task(self, sender, **kwargs):
        """Create periodic task if it doesn't already exist"""
        print("Post-migrate signal received, checking for periodic task creation.")
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        # Check if the periodic task already exists
        if not PeriodicTask.objects.filter(name="Update Binance BTCUSDT Prediction Every 15min").exists():
            print("Periodic task doesn't exist, creating a new one.")
            
            # Create schedule and periodic task
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=15,
                period=IntervalSchedule.MINUTES,
            )
            PeriodicTask.objects.create(
                interval=schedule,
                name='Update Binance BTCUSDT Prediction Every 15min',
                task='crypticron_trade.tasks.update_binance_data_task',  # Replace with your task name
            )
            print("Periodic task created successfully.")
        else:
            print("Periodic task already exists.")
