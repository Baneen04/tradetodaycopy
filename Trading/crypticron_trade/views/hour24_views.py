
from django.shortcuts import render
from django.http import JsonResponse
from crypticron_trade.utils.hour24  import predict_symbol_24h
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def h24_prediction(request):
    symbol = request.GET.get("symbol", "BTCUSDT")  # Default to BTCUSDT if no symbol provided
    predictions = predict_symbol_24h(symbol)
    return JsonResponse({"symbol": symbol, "predictions": predictions})