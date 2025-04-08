# from django.http import FileResponse, HttpResponse
# from crypticron_trade.utils.fear_greed_index import save_fear_greed_chart

# def fear_greed_chart_view(request):
#     """View to generate and return the most recent Fear and Greed Index chart as an image."""
#     file_path, file_url = save_fear_greed_chart()
    
#     if file_path is None:
#         return HttpResponse("Failed to generate chart", status=500)
    
#     return FileResponse(open(file_path, "rb"), content_type="image/png")


from django.http import HttpResponse
from crypticron_trade.utils.fear_greed_index import generate_fear_greed_chart
from crypticron_trade.utils.FG_values import get_fear_greed_index
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fear_greed_chart_view(request):
    """View to generate and return the Fear and Greed Index chart as an image response."""
    img_bytes = generate_fear_greed_chart()

    if img_bytes is None:
        return HttpResponse("Failed to generate chart", status=500)

    return HttpResponse(img_bytes, content_type="image/png")

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fg_index_view(request):
    """Django view that simply calls the function from utils.py."""
    return get_fear_greed_index()
