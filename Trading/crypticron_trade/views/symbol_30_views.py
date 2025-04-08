from django.http import JsonResponse, FileResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from crypticron_trade.utils.symbol_30min import predict_symbol_30
import os
from django.conf import settings

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT authentication
def symbol30_prediction_view(request):
    """
    API endpoint to retrieve the 30-minute price prediction for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        JsonResponse: JSON response containing the predicted values.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if not provided
        predictions = predict_symbol_30(symbol)

        if not isinstance(predictions, dict):  # Validate that predictions are in correct format
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse({"symbol": symbol, "predictions": predictions}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT authentication
def symbol30_linegraph_view(request):
    """
    API endpoint to retrieve the 30-minute prediction line graph for a given trading symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        FileResponse: Image file response containing the prediction graph.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Get symbol from query params (default: BTCUSDT)
        image_path = os.path.join(settings.MEDIA_ROOT, f"{symbol}_30_prediction.png")

        if not os.path.exists(image_path):
            return JsonResponse({"error": f"Graph for {symbol} not found. Ensure predictions are generated."}, status=404)

        return FileResponse(open(image_path, "rb"), content_type="image/png")

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch graph: {str(e)}"}, status=500)
