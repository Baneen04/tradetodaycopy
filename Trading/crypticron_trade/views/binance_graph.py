# from django.http import JsonResponse
# from django.shortcuts import render
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from crypticron_trade.utilsis.live_graph_binance import generate_chart


# import plotly.offline as pyo


# def candlestick_chart_view(request):
#     """ Render BTC/USDT candlestick chart in Django template. """
#     fig = generate_chart()
#     chart_html = pyo.plot(fig, output_type="div")
#     return render(request, "live_chart.html", {"chart": chart_html})



