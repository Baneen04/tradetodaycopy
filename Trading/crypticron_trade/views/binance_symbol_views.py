from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from crypticron_trade.utils.binance_symbol_data import (
    get_binance_symbols_with_ohlc,
    get_binance_symbols_with_interval,
)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def binance_symbols_view(request):
    """
    API endpoint to fetch Binance symbols.

    Returns:
        JsonResponse: JSON response containing symbol name, price, 
                      24h change, 4h change, 24h volume, and market cap.
    """
    try:
        data = get_binance_symbols_with_ohlc()
        if not isinstance(data, list):  # Ensure response is a valid list
            return JsonResponse({"error": "Invalid data format received"}, status=500)

        return JsonResponse({"symbols": data}, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch symbols: {str(e)}"}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def binance_symbols_interval_view(request):
    """
    API endpoint to fetch Binance symbols with OHLC values for a given time interval.

    Query Parameters:
        interval (str): Time interval for OHLC data (default: "1m").

    Returns:
        JsonResponse: JSON response containing symbols and their OHLC values.
    """
    try:
        time_interval = request.GET.get("interval", "1m")  # Default to 1-minute interval
        data = get_binance_symbols_with_interval(time_interval)

        if not isinstance(data, list):  # Ensure response is a valid list
            return JsonResponse({"error": "Invalid data format received"}, status=500)

        return JsonResponse({"symbols": data}, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch symbols for interval {time_interval}: {str(e)}"}, status=500)
