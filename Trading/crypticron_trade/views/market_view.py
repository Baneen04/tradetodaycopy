# from django.shortcuts import render
# from django.http import JsonResponse
# from crypticron_trade.utils.market_text import create_market_prediction_index
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated

# # @api_view(["GET"])
# # @permission_classes([IsAuthenticated])
# def market_prediction_index_view(request):
#     """
#     View to return Market Prediction Index graph as a Base64 string.
#     """
#     img_base64 = create_market_prediction_index()
#     if img_base64 is None:
#         return JsonResponse({"error": "No data available"}, status=500)

#     return JsonResponse({"image": img_base64})

from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from crypticron_trade.utils.market_text import create_market_prediction_index
from crypticron_trade.utils.market_index_val import market_prediction_index
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import base64
import io

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
def market_prediction_index_view(request):
    """
    View to return Market Prediction Index graph directly as an image response.
    """
    img_base64 = create_market_prediction_index()
    
    if img_base64 is None:
        return HttpResponse("No data available", content_type="text/plain", status=500)

    # Decode Base64 string to binary image data
    img_data = base64.b64decode(img_base64)

    return HttpResponse(img_data, content_type="image/png")


def market_index(request):
    """
    Django view to return the market prediction index data.
    """
    data = market_prediction_index()
    
    # if data is None or not isinstance(data, dict):  # Ensure data is a dictionary
    #     return JsonResponse({"error": "No data available"}, status=500)

    return JsonResponse(data)  # Explicitly allow non-dict responses (though it's already a dict)
