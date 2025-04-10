# from django.db import models

# class HistoricalData(models.Model):
#     prediction_time = models.CharField(max_length=10, choices=[('15min', '15 minutes'), ('30min', '30 minutes'), ('1hour', '1 hour')])
#     symbol = models.CharField(max_length=20)
#     timestamp = models.DateTimeField()
#     open_price = models.DecimalField(max_digits=20, decimal_places=5)
#     high_price = models.DecimalField(max_digits=20, decimal_places=5)
#     low_price = models.DecimalField(max_digits=20, decimal_places=5)
#     close_price = models.DecimalField(max_digits=20, decimal_places=5)

#     def __str__(self):
#         return f"{self.symbol} at {self.timestamp}"

# class Prediction(models.Model):
#     prediction_time = models.CharField(max_length=10, choices=[('15min', '15 minutes'), ('30min', '30 minutes'), ('1hour', '1 hour')])
#     symbol = models.CharField(max_length=20)
#     last_actual_price = models.DecimalField(max_digits=20, decimal_places=5)
#     last_time = models.DateTimeField()
#     timestamp = models.DateTimeField(auto_now_add=True) 
#     predicted_price = models.DecimalField(max_digits=20, decimal_places=5)
#     tp1 = models.DecimalField(max_digits=20, decimal_places=5)
#     tp2 = models.DecimalField(max_digits=20, decimal_places=5)
#     sl = models.DecimalField(max_digits=20, decimal_places=5)
#     confidence_interval = models.CharField(max_length=50)
#     confidence_percentage = models.DecimalField(max_digits=5, decimal_places=2)
 
#     def __str__(self):
#         return f"Prediction for {self.symbol} at {self.timestamp} with {self.prediction_time} forecast"



from mongoengine import Document, StringField, DecimalField, DateTimeField, ListField, DictField, EmbeddedDocumentField, FloatField
import datetime

class PredictionResult(Document):
    prediction_time = StringField(choices=['15min', '30min', '1hour'], required=True)
    symbol = StringField(max_length=20, required=True)
    last_actual_price = DecimalField(precision=5, required=True)
    last_time = DateTimeField(required=True)
    timestamps = ListField(DateTimeField())  # or ListField(StringField()) if storing as strings
    predicted_prices = ListField(FloatField())
    tp1_values = ListField(FloatField())
    tp2_values = ListField(FloatField())
    sl_values = ListField(FloatField())
    confidence_intervals = ListField(ListField(FloatField()))  # Example: [[low1, high1], [low2, high2], ...]
    confidence_percentages = ListField(FloatField())
    historical_data = ListField(DictField())  # Or a custom EmbeddedDocument
    created_at = DateTimeField(default=datetime.datetime.utcnow)

