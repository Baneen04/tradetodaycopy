from django.shortcuts import render
from crypticron_trade.utils.min15_chart_prediction import generate_btc_price_chart

def btc_chart_view(request):
    """View to render BTC price chart and predictions with confidence intervals."""
    chart_data = generate_btc_price_chart()  # Fetch chart, predictions, and confidence intervals

    predictions = [
        {
            "timestamp": pred["timestamp"],
            "price": pred["predicted_price"],
            "confidence_interval": pred.get("confidence_interval", 0),  # Default 0 if missing
            "confidence_percentage": pred.get("confidence_percentage", 100)  # Default 100% if missing
        }
        for pred in chart_data["predictions"]
    ]

    return render(request, 'test.html', {
        'chart_html': chart_data["graph_html"],
        'predictions': predictions
    })
