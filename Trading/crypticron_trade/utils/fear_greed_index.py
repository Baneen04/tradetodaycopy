# import requests
# import plotly.graph_objects as go
# from datetime import datetime
# import plotly.io as pio
# import os
# from django.conf import settings
# from glob import glob

# # API URL for Fear and Greed Index
# FEAR_GREED_API = "https://api.alternative.me/fng/"

# def fetch_fear_greed_index():
#     """Fetches the Fear and Greed Index from the API."""
#     response = requests.get(FEAR_GREED_API)
#     if response.status_code == 200:
#         data = response.json()
#         index_value = int(data["data"][0]["value"])
#         index_label = data["data"][0]["value_classification"]
#         last_updated = datetime.utcfromtimestamp(int(data["data"][0]["timestamp"])).strftime('%Y-%m-%d %H:%M UTC')
#         return index_value, index_label, last_updated
#     return None, None, None

# def save_fear_greed_chart():
#     """Generates and saves the Fear and Greed Index chart as a PNG file with a timestamped filename."""
#     index_value, index_label, last_updated = fetch_fear_greed_index()
#     if index_value is None:
#         return None, None

#     # Create the gauge chart
#     fig = go.Figure(go.Indicator(
#         mode="gauge+number",
#         value=index_value,
#         title={"text": f"Fear and Greed Index\n{index_label}"},
#         gauge={
#             "axis": {"range": [0, 100]},
#             "bar": {"color": "black"},
#             "steps": [
#                 {"range": [0, 25], "color": "red"},
#                 {"range": [25, 50], "color": "orange"},
#                 {"range": [50, 75], "color": "lightgreen"},
#                 {"range": [75, 100], "color": "green"}
#             ]
#         }
#     ))

#     fig.update_layout(title=f"Bitcoin Fear and Greed Index (Last Updated: {last_updated})", template="plotly_dark")

#     # Create media directory if it doesn't exist
#     media_path = os.path.join(settings.MEDIA_ROOT, "fear_greed")
#     os.makedirs(media_path, exist_ok=True)

#     # Generate a timestamped filename
#     timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
#     filename = f"fear_greed_{timestamp}.png"
#     file_path = os.path.join(media_path, filename)

#     # Save the image
#     img_bytes = pio.to_image(fig, format="png")
#     with open(file_path, "wb") as f:
#         f.write(img_bytes)

#     return file_path, f"{settings.MEDIA_URL}fear_greed/{filename}"


import requests
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

# API URL for Fear and Greed Index
FEAR_GREED_API = "https://api.alternative.me/fng/"

def fetch_fear_greed_index():
    """Fetches the Fear and Greed Index from the API."""
    response = requests.get(FEAR_GREED_API)
    if response.status_code == 200:
        data = response.json()
        index_value = int(data["data"][0]["value"])
        index_label = data["data"][0]["value_classification"]
        last_updated = datetime.utcfromtimestamp(int(data["data"][0]["timestamp"])).strftime('%Y-%m-%d %H:%M UTC')
        return index_value, index_label, last_updated
    return None, None, None

def generate_fear_greed_chart():
    """Generates the Fear and Greed Index chart and returns it as image bytes."""
    index_value, index_label, last_updated = fetch_fear_greed_index()
    if index_value is None:
        return None

    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=index_value,
        title={"text": f"Fear and Greed Index\n{index_label}"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "black"},
            "steps": [
                {"range": [0, 25], "color": "red"},
                {"range": [25, 50], "color": "orange"},
                {"range": [50, 75], "color": "lightgreen"},
                {"range": [75, 100], "color": "green"}
            ]
        }
    ))

    fig.update_layout(title=f"Bitcoin Fear and Greed Index (Last Updated: {last_updated})", template="plotly_dark")

    # Convert plotly figure to PNG bytes
    img_bytes = pio.to_image(fig, format="png")

    return img_bytes
