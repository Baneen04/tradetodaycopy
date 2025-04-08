from django.http import JsonResponse, FileResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import os
from crypticron_trade.utils.min_15 import predict_btc_15  # Ensure this function is implemented correctly


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def min15_prediction_view(request):
    """
    API endpoint to retrieve 15-minute Bitcoin price predictions.

    Returns:
        JsonResponse: JSON response containing the predicted BTC prices.
    """
    try:
        predictions = predict_btc_15()

        if not isinstance(predictions, dict):
            return JsonResponse({"error": "Invalid prediction format"}, status=500)

        return JsonResponse(predictions, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def min15_linegraph_view(request):
    """
    API endpoint to retrieve the 15-minute prediction line graph.

    Returns:
        FileResponse: The prediction graph image if available.
        JsonResponse: Error message if the file is missing.
    """
    image_filename = "15min_prediction.png"
    image_path = os.path.join(settings.MEDIA_ROOT, image_filename)

    if not os.path.exists(image_path):
        return JsonResponse(
            {"error": f"Graph '{image_filename}' not found. Ensure predictions are being generated and saved properly."},
            status=404
        )

    try:
        return FileResponse(open(image_path, "rb"), content_type="image/png")
    except Exception as e:
        return JsonResponse({"error": f"Error loading graph: {str(e)}"}, status=500)
