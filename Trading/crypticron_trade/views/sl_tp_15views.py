from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from crypticron_trade.utils.SL_TP_15min import get_SLTP_prediction


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def SLTP_15view(request):
    """
    API endpoint to retrieve 15-minute BTC price predictions with TP1, TP2, and SL.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        JsonResponse: JSON response containing the predictions.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if no symbol is provided
        predictions = get_SLTP_prediction(symbol)

        if not isinstance(predictions, dict):  # Ensure predictions are in a valid JSON format
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse({"predictions": predictions}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)
