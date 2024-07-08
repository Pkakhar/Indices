import yfinance as yf
import requests
import xml.etree.ElementTree as ET

def get_quote(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    return response.json()["Global Quote"]

def get_index_data(index_symbol):
    index = yf.Ticker(index_symbol)
    data = index.history(period='1d')
    latest = data.iloc[-1]
    return {
        'symbol': index_symbol,
        'open': latest['Open'],
        'high': latest['High'],
        'low': latest['Low'],
        'price': latest['Close'],
        'change': latest['Close'] - latest['Open'],
        'change_percent': ((latest['Close'] - latest['Open']) / latest['Open']) * 100
    }

def create_rss(quotes):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    title = ET.SubElement(channel, 'title')
    title.text = 'Live Stock Indices Updates'
    
    for quote in quotes:
        item = ET.SubElement(channel, 'item')
        title = ET.SubElement(item, 'title')
        title.text = f"{quote['symbol']} - {quote['price']}"
        description = ET.SubElement(item, 'description')
        description.text = f"Open: {quote['open']}, High: {quote['high']}, Low: {quote['low']}, Change: {quote['change']} ({quote['change_percent']}%)"
    
    return ET.tostring(rss, encoding='utf-8').decode('utf-8')

# Your Alpha Vantage API Key
api_key = 'ZBP2BVNFUX93H5TL'

# Symbols for the indices
alpha_vantage_symbols = ['^N225', '^IXIC', '^INX']
yfinance_symbols = ['^NSEI', '^BSESN']

# Fetch data from Alpha Vantage
quotes = []
for symbol in alpha_vantage_symbols:
    quote = get_quote(symbol, api_key)
    quotes.append({
        'symbol': quote["01. symbol"],
        'open': quote["02. open"],
        'high': quote["03. high"],
        'low': quote["04. low"],
        'price': quote["05. price"],
        'change': quote["09. change"],
        'change_percent': quote["10. change percent"]
    })

# Fetch data for Nifty 50 and Sensex from Yahoo Finance
for symbol in yfinance_symbols:
    quotes.append(get_index_data(symbol))

rss_feed = create_rss(quotes)

# Save RSS feed to file
with open("index.xml", "w") as file:
    file.write(rss_feed)

print("RSS feed generated and saved as index.xml")
