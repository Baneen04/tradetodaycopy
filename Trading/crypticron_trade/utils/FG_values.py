import requests
from datetime import datetime
from django.http import JsonResponse

# API URL for Fear and Greed Index
FEAR_GREED_API = "https://api.alternative.me/fng/"

def get_fear_greed_index():
    """Fetches the Fear and Greed Index and returns a JSON response."""
    try:
        response = requests.get(FEAR_GREED_API, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "data" in data and data["data"]:
            index_value = int(data["data"][0]["value"])
            index_label = data["data"][0]["value_classification"]
            last_updated = datetime.utcfromtimestamp(int(data["data"][0]["timestamp"])).strftime('%Y-%m-%d %H:%M UTC')

            return JsonResponse({
                "index_value": index_value,
                "index_label": index_label,
                "last_updated": last_updated
            })
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching Fear and Greed Index: {e}")

    return JsonResponse({"error": "Failed to fetch Fear and Greed Index"}, status=500)
