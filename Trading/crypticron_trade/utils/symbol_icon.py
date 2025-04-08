import requests
from bs4 import BeautifulSoup

# URL of the webpage you want to scrape
url = "https://www.binance.com/en/price/"  # Replace with the actual URL

# Send an HTTP GET request to fetch the page content
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Find all cryptocurrency entries
crypto_list = soup.find_all("div", class_="css-3tf3mo")

# Extract data
cryptos = []
for crypto in crypto_list:
    try:
        rank = crypto.find("div", class_="css-1jmr5yu").text
        name = crypto.find("div", class_="css-11aussz").text
        ticker = crypto.find("div", class_="css-pl05v3").text
        image_url = crypto.find("img")["src"]
        
        cryptos.append({"Rank": rank, "Name": name, "Ticker": ticker, "Image URL": image_url})
    except AttributeError:
        continue  # Skip if any data is missing

# Display extracted data
for coin in cryptos[:10]:  # Show only top 10 results
    print(coin)
