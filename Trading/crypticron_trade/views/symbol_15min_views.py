from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from crypticron_trade.utils.symbol_15_values import get_latest_prediction  # Import the function

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT token
def min15_prediction(request):
    """
    API endpoint to retrieve the latest 15-minute price prediction for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        JsonResponse: JSON response containing the symbol and predicted values.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if not provided
        predictions = get_latest_prediction(symbol)

        # if not isinstance(predictions, dict):  # Ensure predictions are in valid JSON format
        # return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse({"symbol": symbol, "predictions": predictions}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)
