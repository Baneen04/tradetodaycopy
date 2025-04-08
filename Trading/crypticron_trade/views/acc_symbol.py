from django.http import JsonResponse, FileResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import os
from crypticron_trade.utils.acc_15min import predict_15crypto  # Import the function
from crypticron_trade.utils.acc_30min import get_predictions
from crypticron_trade.utils.acc_1h import predict_symbol_1h

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT token
def prediction_acc(request):
    """
    API endpoint to retrieve 15-minute price predictions for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)
        interval (str): Time interval (default: 15m)

    Returns:
        JsonResponse: JSON response containing predicted values.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default symbol is BTCUSDT
        predictions = predict_15crypto (symbol)

        if not isinstance(predictions, dict):  # Ensure predictions are JSON serializable
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse(predictions, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)
    



@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT authentication
def prediction_30acc(request):
    """
    API endpoint to retrieve the 30-minute price prediction for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        JsonResponse: JSON response containing the predicted values.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if not provided
        predictions = get_predictions(symbol)

        if not isinstance(predictions, dict):  # Validate that predictions are in correct format
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse({"symbol": symbol, "predictions": predictions}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT authentication
def prediction_1hacc(request):
    """
    API endpoint to retrieve the 30-minute price prediction for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        JsonResponse: JSON response containing the predicted values.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if not provided
        predictions = predict_symbol_1h(symbol)

        if not isinstance(predictions, dict):  # Validate that predictions are in correct format
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse({"symbol": symbol, "predictions": predictions}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)