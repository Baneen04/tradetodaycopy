from django.shortcuts import render

def candlestick_chart(request):
    return render(request, "pre.html")


def update_chart(request):
    return render(request, "update.html")
