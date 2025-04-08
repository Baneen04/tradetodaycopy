from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from crypticron_trade.utils.SL_TP_30min import get_predictions


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def SLTP_30view(request):
    """
    API endpoint to retrieve 30-minute BTC price predictions with TP1, TP2, and SL.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        JsonResponse: JSON response containing predictions.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if no symbol is provided
        predictions = get_predictions(symbol)

        if not isinstance(predictions, dict):  # Ensure the predictions are in a JSON-serializable format
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse({"predictions": predictions}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)
