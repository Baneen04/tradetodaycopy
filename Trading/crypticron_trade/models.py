from django.db import models

class HistoricalData(models.Model):
    prediction_time = models.CharField(max_length=10, choices=[('15min', '15 minutes'), ('30min', '30 minutes'), ('1hour', '1 hour')])
    symbol = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=5)
    high_price = models.DecimalField(max_digits=20, decimal_places=5)
    low_price = models.DecimalField(max_digits=20, decimal_places=5)
    close_price = models.DecimalField(max_digits=20, decimal_places=5)

    def __str__(self):
        return f"{self.symbol} at {self.timestamp}"

class Prediction(models.Model):
    prediction_time = models.CharField(max_length=10, choices=[('15min', '15 minutes'), ('30min', '30 minutes'), ('1hour', '1 hour')])
    symbol = models.CharField(max_length=20)
    last_actual_price = models.DecimalField(max_digits=20, decimal_places=5)
    last_time = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True) 
    predicted_price = models.DecimalField(max_digits=20, decimal_places=5)
    tp1 = models.DecimalField(max_digits=20, decimal_places=5)
    tp2 = models.DecimalField(max_digits=20, decimal_places=5)
    sl = models.DecimalField(max_digits=20, decimal_places=5)
    confidence_interval = models.CharField(max_length=50)
    confidence_percentage = models.DecimalField(max_digits=5, decimal_places=2)
 
    def __str__(self):
        return f"Prediction for {self.symbol} at {self.timestamp} with {self.prediction_time} forecast"
