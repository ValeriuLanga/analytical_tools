import requests
import json

import utils

def get_eod_data(symbol: str):
    api_key = utils.load_eod_data_api_key()['key']

    url = f'https://eodhd.com/api/eod/{symbol}?from=2023-07-07&to=2024-01-01&period=d&api_token={api_key}&fmt=json'
    data = requests.get(url).json()

    print(data)


get_eod_data('MSFT')