from django.shortcuts import render
from django.http import JsonResponse
from crypticron_trade.utils.symbol_1h_value import get_crypto_prediction_data
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def h1_prediction(request):
    symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if no symbol provided
    predictions = get_crypto_prediction_data(symbol)
    return JsonResponse({"symbol": symbol, "predictions": predictions})