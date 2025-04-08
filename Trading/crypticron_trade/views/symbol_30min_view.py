from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from crypticron_trade.utils.symbol_30_values import get_predictions

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def min30_prediction(request):
    """
    API endpoint to fetch 30-minute price predictions for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        JsonResponse: JSON response containing the symbol and its predicted values.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT").upper()  # Default to BTCUSDT if not provided
        predictions = get_predictions(symbol)

        if not isinstance(predictions, dict):  # Ensure the response format is valid
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse({"symbol": symbol, "predictions": predictions}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)
