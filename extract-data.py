import pandas as pd
import requests


# API Key
api_key = 'Jlv9nG6xEQHbF9MIY2NkzSasVOVe50I6'

# Request currencies API
url = 'https://api.currencybeacon.com/v1/currencies?api_key=' + api_key +'&type=fiat'

# Get the data from the API
response = requests.get(url)
data = response.json()['response']

# Create a list to store the currency names and short codes
currency_symbols = []
for currency in data:
    currency_symbols.append([currency['name'], currency['short_code']])

# Convert the list to a DataFrame
df = pd.DataFrame(currency_symbols, columns=['name', 'short_code'])

# Save the DataFrame to a CSV file
df.to_csv('./data/' + 'currency_shortcodes.csv', index=False)

