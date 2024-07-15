# import pandas as pd
import json
import utils

from pathlib import Path

from coinbase.rest import RESTClient
from datetime import datetime


def get_candles(product_id: str) -> dict:
    cdp_api_key = utils.load_api_key()

    client = RESTClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'])

    start_date = datetime.strptime('2024-05-13', "%Y-%m-%d")
    print(start_date.timestamp())
    end_date = datetime.strptime('2024-07-13', "%Y-%m-%d")
    print(end_date.timestamp())

    ticks = client.get_candles(
            product_id=product_id, 
            start=int(start_date.timestamp()), 
            end=int(end_date.timestamp()), 
            granularity='SIX_HOUR'
            )
    
    return ticks


def get_products(save_to_json=False) -> list[dict]:
    '''
    load_archived_data=True avoids an API call 

    A single entry will look like this:
    {
        'product_id': 'SOL-USDC', 
        'price': '146.55', 
        'price_percentage_change_24h': '4.82832618025751', 
        'volume_24h': '644595.03677692', 
        'volume_percentage_change_24h': '12.31750359590964', 
        'base_increment': '0.00000001', 
        'quote_increment': '0.01', 
        'quote_min_size': '1', 
        'quote_max_size': '25000000', 
        'base_min_size': '0.00000001', 
        'base_max_size': '1274000', 
        'base_name': 'Solana', 
        'quote_name': 'USDC', 
        'watched': False, 
        'is_disabled': False, 
        'new': False, 
        'status': 'online', 
        'cancel_only': False, 
        'limit_only': False, 
        'post_only': False, 
        'trading_disabled': False, 
        'auction_mode': False, 
        'product_type': 'SPOT', 
        'quote_currency_id': 'USDC', 
        'base_currency_id': 'SOL', 
        'fcm_trading_session_details': None, 
        'mid_market_price': '', 
        'alias': 'SOL-USD', 
        'alias_to': [], 
        'base_display_symbol': 'SOL', 
        'quote_display_symbol': 'USD', 
        'view_only': False, 
        'price_increment': '0.01', 
        'display_name': 'SOL-USDC', 
        'product_venue': 'CBE', 
        'approximate_quote_24h_volume': '94465402.64'}
    '''
    cdp_api_key = utils.load_api_key()
    file_name = 'products_{}.json'.format(datetime.now().date())
    dump_file = Path('data\\' + file_name)
    
    client = RESTClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'])
    products = client.get_products()
    print("[INFO] Sourced {} products".format(products['num_products']))

    if (save_to_json):
        file_name = 'products_{}.json'.format(datetime.now().date())
        dump_file = Path('data\\' + file_name)
        
        if (not dump_file.is_file()):
            with open(dump_file, 'w') as fp:
                json.dump(products['products'], fp)
                print("[INFO] Wrote {} products to {}".format(products['num_products'], dump_file))

    return products['products']

def get_archived_product_data(date: str) -> dict:
    '''
    date must be in YYYY-MM-DD format
    '''

    file_name = 'products_{}.json'.format(date)
    
    dump_file = Path('data\\' + file_name)
    if (not dump_file.is_file()):
        print("[INFO] invalid archive file: {}".format(file_name))

    with open(dump_file, 'r') as fp:    
        data = json.load(fp)
        print("[INFO] Loaded {} products from {}".format(len(data), dump_file))

    return data