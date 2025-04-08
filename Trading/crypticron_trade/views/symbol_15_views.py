from django.http import JsonResponse, FileResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import os
from crypticron_trade.utils.symbol_15min import predict_allcrypto  # Import the function


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT token
def symbol15_prediction_view(request):
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
        # interval = request.GET.get("interval", "15m")  # Default interval is 15m
        predictions = predict_allcrypto(symbol)

        if not isinstance(predictions, dict):  # Ensure predictions are JSON serializable
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse(predictions, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch predictions: {str(e)}"}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Require JWT token
def symbol15_linegraph_view(request):
    """
    API endpoint to retrieve the 15-minute prediction line graph for a given symbol.

    Query Parameters:
        symbol (str): Trading symbol (default: BTCUSDT)

    Returns:
        FileResponse: The prediction graph image if available.
        JsonResponse: Error message if the file is missing.
    """
    try:
        symbol = request.GET.get("symbol", "BTCUSDT")  # Default symbol is BTCUSDT
        image_filename = f"{symbol}_prediction.png"
        image_path = os.path.join(settings.MEDIA_ROOT, image_filename)

        if not os.path.exists(image_path):
            return JsonResponse(
                {"error": f"Graph for {symbol} not found. Ensure predictions are generated."},
                status=404
            )

        return FileResponse(open(image_path, "rb"), content_type="image/png")

    except Exception as e:
        return JsonResponse({"error": f"Failed to load graph: {str(e)}"}, status=500)
