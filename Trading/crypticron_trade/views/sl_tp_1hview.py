from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from crypticron_trade.utils.SL_TP_1h import get_crypto_prediction_data


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def SLTP_1hview(request):
    """
    API endpoint to retrieve 15-minute BTC price predictions with TP1, TP2, and SL.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        JsonResponse: JSON response containing the predictions.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if no symbol is provided
        predictions = get_crypto_prediction_data(symbol)

        return JsonResponse({"predictions": predictions}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)
