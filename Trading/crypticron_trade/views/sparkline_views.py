from django.http import JsonResponse
from crypticron_trade.utils.spark_line import fetch_sparkline_data, fetch_multiple_sparklines
from django.views.decorators.csrf import csrf_exempt  # Import CSRF exemption


@csrf_exempt
def get_sparkline_data(request):
    """
    Django view to return sparkline data for a single symbol.
    """
    symbol = request.GET.get("symbol", "BTCUSDT") 
    data = fetch_sparkline_data(symbol)
    return JsonResponse(data)
@csrf_exempt
# def get_multiple_sparklines(request):
#     """
#     Django view to return sparkline data for multiple symbols.
#     """
#     data = fetch_multiple_sparklines()
#     return JsonResponse(data)

def get_multiple_sparklines(request):
    data = fetch_multiple_sparklines()
    return JsonResponse(data, safe=False)  # safe=False allows list response
