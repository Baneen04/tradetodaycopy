# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# from binance.client import Client
# import seaborn as sns
# from matplotlib.patches import Polygon
# import time
# from matplotlib.ticker import PercentFormatter

# def get_binance_data_top_100(api_key, api_secret, lookback_hours=24):
#     """
#     Get price data from Binance API for top 100 symbols by volume
#     """
#     client = Client(api_key, api_secret)
#     print("Connected to Binance. Fetching top symbols...")
    
#     # Get all tickers and sort by volume to find top 100
#     tickers = client.get_ticker()
#     sorted_tickers = sorted(tickers, key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
#     top_symbols = [ticker['symbol'] for ticker in sorted_tickers[:100]]
    
#     print(f"Fetching data for top 100 symbols...")
#     start_time = time.time()
    
#     # Get current and historical prices for each symbol
#     data = []
#     for i, symbol in enumerate(top_symbols):
#         if i % 10 == 0:
#             print(f"Processing {i+1}-{min(i+10, 100)} of 100 symbols...")
        
#         try:
#             # Get current price
#             ticker = client.get_ticker(symbol=symbol)
#             current_price = float(ticker['lastPrice'])
            
#             # Get historical price from lookback_hours ago
#             klines = client.get_historical_klines(
#                 symbol, Client.KLINE_INTERVAL_1HOUR, 
#                 f"{lookback_hours} hours ago UTC",
#                 limit=1  # Just get one candle for efficiency
#             )
#             if klines:
#                 historical_price = float(klines[0][4])  # Close price of first candle
                
#                 # Calculate percentage change
#                 percent_change = ((current_price - historical_price) / historical_price) * 100
                
#                 data.append({
#                     'symbol': symbol,
#                     'percent_change': percent_change
#                 })
#         except Exception as e:
#             print(f"Error processing {symbol}: {e}")
    
#     elapsed_time = time.time() - start_time
#     print(f"Data collection complete. Processed {len(data)} symbols in {elapsed_time:.2f} seconds.")
    
#     return pd.DataFrame(data)

# def create_market_prediction_index_improved(df):
#     """
#     Create a smoother Market Prediction Index visualization matching Image 2
#     """
#     print("Creating visualization...")
    
#     # Set dark theme with specific colors matching the image
#     plt.style.use('dark_background')
    
#     # Set up the figure with rounded corners
#     fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1e2130')
#     ax.set_facecolor('#1e2130')
    
#     # Calculate prediction line position (use median as in the image)
#     prediction_line = df['percent_change'].median()
#     prediction_line_formatted = f"{prediction_line:.2f}%"
    
#     # Get recommendation based on median value
#     recommendation = "Sell" if prediction_line < 0 else "Buy"
    
#     # Create KDE plot for a smoother histogram look (as in Image 2)
#     # First create the bins
#     bins = np.linspace(-6, 6, 100)
    
#     # Calculate histogram values
#     hist, bin_edges = np.histogram(df['percent_change'], bins=bins, density=True)
#     bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
#     # Smooth the histogram (similar to KDE effect)
#     from scipy.ndimage import gaussian_filter1d
#     hist_smooth = gaussian_filter1d(hist, sigma=1.5)
    
#     # Scale to make it look similar to the reference
#     hist_smooth = hist_smooth * 15  # Adjust this scale factor as needed
    
#     # Plot the histogram as a continuous area
#     for i in range(len(bin_centers) - 1):
#         if bin_centers[i] < prediction_line:
#             ax.fill_between([bin_centers[i], bin_centers[i+1]], 
#                            [0, 0], 
#                            [hist_smooth[i], hist_smooth[i+1]], 
#                            color='#f05654', alpha=0.8)  # Red for negative
#         else:
#             ax.fill_between([bin_centers[i], bin_centers[i+1]], 
#                            [0, 0], 
#                            [hist_smooth[i], hist_smooth[i+1]], 
#                            color='#41c6ba', alpha=0.8)  # Teal for positive
    
#     # Add the prediction line
#     ax.axvline(x=prediction_line, color='#808080', linestyle='-', alpha=0.7, zorder=5)
    
#     # Add a small box for the prediction value (similar to Image 2)
#     ax.text(prediction_line, max(hist_smooth)*0.8, prediction_line_formatted, 
#             ha='center', va='center', fontsize=10, color='white',
#             bbox=dict(facecolor='#1e2130', edgecolor='white', alpha=0.8, 
#                      boxstyle='round,pad=0.3', linewidth=1))
    
#     # Create triangle marker below the x-axis
#     triangle_y = -max(hist_smooth) * 0.1
#     triangle = Polygon([
#         [prediction_line, triangle_y*0.5], 
#         [prediction_line - 0.15, triangle_y*1.5], 
#         [prediction_line + 0.15, triangle_y*1.5]
#     ], closed=True, facecolor='lightgray', zorder=10)
#     ax.add_patch(triangle)
    
#     # Add recommendation text
#     ax.text(prediction_line, triangle_y*2.5, recommendation, 
#             ha='center', va='center', fontsize=16, color='white', 
#             fontweight='bold', zorder=10)
    
#     # Configure axes
#     ax.set_xlim(-6, 6)
#     ax.set_xticks([-6.0, -3.0, 0, 3.0, 6.0])
#     ax.set_xticklabels(['-6.0%', '-3.0%', '0%', '3.0%', '6.0%'])
    
#     # Remove y-ticks to match Image 2
#     ax.set_yticks([])
    
#     # Add subtle horizontal line at y=0
#     ax.axhline(y=0, color='#808080', linestyle='-', alpha=0.3, linewidth=0.5)
    
#     # Remove most of the spines to match Image 2
#     for spine in ['top', 'right', 'left']:
#         ax.spines[spine].set_visible(False)
#     ax.spines['bottom'].set_color('#808080')
#     ax.spines['bottom'].set_alpha(0.3)
    
#     # Add titles in the correct position and style
#     plt.suptitle('Market Prediction Index', fontsize=18, y=0.95, color='white', fontweight='medium')
#     plt.title('Distribution of the market predictions of the percentage\nchange in price.', 
#               fontsize=11, pad=10, color='#d0d0d0')
    
#     # Add rounded corners effect by adding a background patch
#     # (This is a visual approximation; for true rounded corners, need to save as image and process)
    
#     plt.tight_layout()
#     return fig

# def main(api_key, api_secret):
#     # Get data from Binance
#     df = get_binance_data_top_100(api_key, api_secret)
    
#     # Create and show the visualization with the improved style
#     fig = create_market_prediction_index_improved(df)
#     plt.savefig('market_prediction_index.png', facecolor='#1e2130', dpi=300, bbox_inches='tight')
#     plt.show()
    
#     # Print summary
#     buy_count = sum(df['percent_change'] > 0)
#     sell_count = sum(df['percent_change'] < 0)
#     print(f"\nBuy signals: {buy_count}, Sell signals: {sell_count}")
#     print(f"Recommendation: {'Buy' if buy_count > sell_count else 'Sell'}")

# # Usage example:
# if __name__ == "__main__":
#     API_KEY = '8jfloPGO8BLaw4CFwfju0PRMadkmD5lcepaWVyaVlr7B2YQJo7w8QuxRUIR9MKZq'
#     API_SECRET = "Q4tPFHzZpD8xJYRvZ4doXeynDpqmPFZ7Bnq4H5IrMN9YcnSoK1aCJoVXO01yJ7bm" 
#     main(API_KEY, API_SECRET)



import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from binance.client import Client
from matplotlib.patches import Polygon
from scipy.ndimage import gaussian_filter1d
import io
import base64
import time
from django.conf import settings

#Binance key
API_KEY = settings.API_KEY
B_SECRET_KEY= settings.B_SECRET_KEY
client = Client(API_KEY, B_SECRET_KEY)

def get_binance_data_top_100():
    """
    Fetch top 100 Binance symbols by volume and compute their percentage change in price.
    """
    
    tickers = client.get_ticker()
    sorted_tickers = sorted(tickers, key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
    top_symbols = [ticker['symbol'] for ticker in sorted_tickers[:100]]

    data = []
    for symbol in top_symbols:
        try:
            # Get current price
            ticker = client.get_ticker(symbol=symbol)
            current_price = float(ticker['lastPrice'])

            # Get historical price (24 hours ago)
            klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, "24 hours ago UTC", limit=1)
            if klines:
                historical_price = float(klines[0][4])  # Close price
                percent_change = ((current_price - historical_price) / historical_price) * 100
                
                data.append({'symbol': symbol, 'percent_change': percent_change})
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    return pd.DataFrame(data)

def create_market_prediction_index():
    """
    Generate the Market Prediction Index graph and return it as a Base64 string.
    """
    df = get_binance_data_top_100()
    
    if df.empty:
        return None  # Return None if no data available

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1e2130')
    ax.set_facecolor('#1e2130')

    prediction_line = df['percent_change'].median()
    recommendation = "Sell" if prediction_line < 0 else "Buy"

    bins = np.linspace(-6, 6, 100)
    hist, bin_edges = np.histogram(df['percent_change'], bins=bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    hist_smooth = gaussian_filter1d(hist, sigma=1.5) * 15

    for i in range(len(bin_centers) - 1):
        color = '#f05654' if bin_centers[i] < prediction_line else '#41c6ba'
        ax.fill_between([bin_centers[i], bin_centers[i+1]], [0, 0], [hist_smooth[i], hist_smooth[i+1]], color=color, alpha=0.8)

    ax.axvline(x=prediction_line, color='#808080', linestyle='-', alpha=0.7, zorder=5)
    ax.text(prediction_line, max(hist_smooth) * 0.8, f"{prediction_line:.2f}%", ha='center', fontsize=10, color='white',
            bbox=dict(facecolor='#1e2130', edgecolor='white', alpha=0.8, boxstyle='round,pad=0.3', linewidth=1))

    triangle_y = -max(hist_smooth) * 0.1
    triangle = Polygon([[prediction_line, triangle_y*0.5], [prediction_line - 0.15, triangle_y*1.5], 
                        [prediction_line + 0.15, triangle_y*1.5]], closed=True, facecolor='lightgray', zorder=10)
    ax.add_patch(triangle)
    ax.text(prediction_line, triangle_y*2.5, recommendation, ha='center', fontsize=16, color='white', fontweight='bold', zorder=10)

    ax.set_xlim(-6, 6)
    ax.set_xticks([-6, -3, 0, 3, 6])
    ax.set_xticklabels(['-6%', '-3%', '0%', '3%', '6%'])
    ax.set_yticks([])

    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#808080')
    ax.spines['bottom'].set_alpha(0.3)

    plt.suptitle('Market Prediction Index', fontsize=18, y=0.95, color='white', fontweight='medium')
    plt.title('Distribution of market predictions based on percentage change.', fontsize=11, pad=10, color='#d0d0d0')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', facecolor='#1e2130', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64
