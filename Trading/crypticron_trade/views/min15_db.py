from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from crypticron_trade.models import Prediction, HistoricalData
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time
from crypticron_trade.utils.min_15m_db  import predict_15crypto  # This is your prediction function
# Define a background task to run the prediction every 15 minutes
def start_background_prediction():
    while True:
        predict_15crypto()  # Generate a prediction every 15 minutes
        time.sleep(900)  # Sleep for 15 minutes (900 seconds)

@csrf_exempt
def start_prediction(request):
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")
        # Step 1: Trigger immediate prediction
        predict_15crypto(symbol)
        print('saveed')
        # Step 2: Start background prediction task
        thread = threading.Thread(target=start_background_prediction)
        thread.daemon = True  # Ensure the thread terminates when the main program exits
        thread.start()

        return JsonResponse({"status": "success", "message": "Prediction started and background task running."})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])    
def latest_prediction(request):
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")
        # Get latest 15 prediction entries (most recent first)
        predictions = Prediction.objects.filter(prediction_time="15min" , symbol=symbol).first()
        results = []
        results.append({
                "predicted_price": predictions.predicted_price,
                "timestamp": predictions.timestamp,
                "tp1": predictions.tp1,
                "tp2": predictions.tp2,
                "sl": predictions.sl,
                "confidence": predictions.confidence_percentage,
                "confidence_interval": predictions.confidence_interval,
                "last_actual_price": predictions.last_actual_price,

            })
        historical = HistoricalData.objects.filter(prediction_time="15min" , symbol=symbol)

        historical_d = []
        for item in historical:
            historical_d.append({
                    'timestamp':item.timestamp,
                    'open_price':item.open_price,
                    'high_price':item.high_price,
                    'low_price':item.low_price,
                    'close_price':item.close_price

            })
            # Try to fetch corresponding historical data
            # historical = HistoricalData.objects.filter(
            #     symbol=item.symbol,
            #     timestamp=item.timestamp,
            #     prediction_time="15min"
            # ).first()

            # historical_data = {
            #     "open": historical.open_price if historical else None,
            #     "high": historical.high_price if historical else None,
            #     "low": historical.low_price if historical else None,
            #     "close": historical.close_price if historical else None,
            # } if historical else {}



        return JsonResponse({
            "status": "success",                
            "symbol": symbol,
            "last_actual_price":predictions.last_actual_price,
            "last_time":predictions.last_time,
            "historical_data": historical_d,
            "prediction": results})
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
