from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
# from crypticron_trade.models import Prediction, HistoricalData
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time
from crypticron_trade.utils.min_15m_db  import get_prediction_from_db, store_prediction 
from crypticron_trade.utils.min_30m_db import get_30prediction_from_db, save30m_predictions
from crypticron_trade.utils.h_1_db import save_symbol_1h, get_1prediction_from_db# This is your prediction function
# Define a background task to run the prediction every 15 minutes
# def start_background_prediction():
#     while True:
#         predict_15crypto()  # Generate a prediction every 15 minutes
#         time.sleep(900)  # Sleep for 15 minutes (900 seconds)

# @csrf_exempt
# def start_prediction(request):
#     try:
#         symbol = request.GET.get("symbol", "BTCUSDT")
#         # Step 1: Trigger immediate prediction
#         predict_15crypto(symbol)
#         print('saveed')
#         # Step 2: Start background prediction task
#         thread = threading.Thread(target=start_background_prediction)
#         thread.daemon = True  # Ensure the thread terminates when the main program exits
#         thread.start()

#         return JsonResponse({"status": "success", "message": "Prediction started and background task running."})

#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT token
def symbol15_db_view(request):
    """
    API endpoint to retrieve 15-minute price predictions for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)
        interval (str): Time interval (default: 15m)

    Returns:
        JsonResponse: JSON response containing predicted values.
    """
    symbol = request.GET.get("symbol", "BTCUSDT")  # Default symbol is BTCUSDT
        # interval = request.GET.get("interval", "15m")  # Default interval is 15m
    predictions = get_prediction_from_db(symbol)

    # if not isinstance(predictions, dict):  # Ensure predictions are JSON serializable
    #     return JsonResponse({"error": "Invalid prediction format"}, status=500)

    return JsonResponse(predictions, status=200, safe=False)

    
from django.views import View
class StorePredictionView(View):
    def get(self, request):
        symbol = request.GET.get('symbol', 'BTCUSDT')  # Default to 'BTCUSDT' if no symbol is provided
        store_prediction(symbol)  # Call store_prediction function with symbol
        return JsonResponse({"message": "Prediction saved successfully!"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT token
def symbol30_db_view(request):
    """
    API endpoint to retrieve 15-minute price predictions for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)
        interval (str): Time interval (default: 15m)

    Returns:
        JsonResponse: JSON response containing predicted values.
    """
    symbol = request.GET.get("symbol", "BTCUSDT")  # Default symbol is BTCUSDT
        # interval = request.GET.get("interval", "15m")  # Default interval is 15m
    predictions = get_30prediction_from_db(symbol)

    # if not isinstance(predictions, dict):  # Ensure predictions are JSON serializable
    #     return JsonResponse({"error": "Invalid prediction format"}, status=500)

    return JsonResponse(predictions, status=200, safe=False)

    
from django.views import View
class Store30PredictionView(View):
    def get(self, request):
        symbol = request.GET.get('symbol', 'BTCUSDT')  # Default to 'BTCUSDT' if no symbol is provided
        save30m_predictions(symbol)  # Call store_prediction function with symbol
        return JsonResponse({"message": "Prediction saved successfully!"})
    


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT token
def symbol1h_db_view(request):
    """
    API endpoint to retrieve 15-minute price predictions for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)
        interval (str): Time interval (default: 15m)

    Returns:
        JsonResponse: JSON response containing predicted values.
    """
    symbol = request.GET.get("symbol", "BTCUSDT")  # Default symbol is BTCUSDT
        # interval = request.GET.get("interval", "15m")  # Default interval is 15m
    predictions = get_1prediction_from_db(symbol)

    # if not isinstance(predictions, dict):  # Ensure predictions are JSON serializable
    #     return JsonResponse({"error": "Invalid prediction format"}, status=500)

    return JsonResponse(predictions, status=200, safe=False)

    
from django.views import View
class Store1hPredictionView(View):
    def get(self, request):
        symbol = request.GET.get('symbol', 'BTCUSDT')  # Default to 'BTCUSDT' if no symbol is provided
        save_symbol_1h(symbol)  # Call store_prediction function with symbol
        return JsonResponse({"message": "Prediction saved successfully!"})