# import pandas as pd
import json
import utils
import os

import pandas as pd

from pathlib import Path
from coinbase.rest import RESTClient
from datetime import datetime


def get_candles(product_pair: str, retry_count=4) -> dict:
    """
    Args:
        product_pair: str
            crypto_id-fiat_ccy pair; see get_products().
        retry_count: int
            Number of retries before we fail the request. Needed because of 
            arbitrary API failures on subsequent requests.
    """

    cdp_api_key = utils.load_coinbase_api_key()
    
    while (True):
        try:
            if (retry_count <= 0):
                # return {}   # TODO: decide on approach for market_data methods - throw, empty, err code
                raise Exception("Failed to load market data candles!")
            
            client = RESTClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'])

            start_date = datetime.strptime('2024-05-13', "%Y-%m-%d")
            end_date = datetime.strptime('2024-07-13', "%Y-%m-%d")

            ticks = client.get_candles(
                    product_id=product_pair, 
                    start=int(start_date.timestamp()), 
                    end=int(end_date.timestamp()), 
                    granularity='SIX_HOUR'
                    )
            
            return ticks
        except: 
            print("[WARN] Failed to get market data!")
            retry_count -= 1


def get_archived_candles(product_pair: str) -> pd.DataFrame:
    archive_path = "data\\{}.parquet".format(product_pair)
    print("[INFO] archive_path = {}".format(archive_path))

    archive_file = Path(archive_path)
    if (not archive_file.is_file()):
        raise Exception("Archive File does NOT exist at {} ! Archive the data before attempting to load!"
                        .format(archive_path))
    
    return pd.read_parquet(archive_path)


def archive_candles(market_data: pd.DataFrame, product_pair: str) -> None:
    """
    Args:
        market_data: DataFrame

        product_pair: str
            crypto_id-fiat_ccy pair; see get_products().
    """
     
    archive_path = "data\\{}.parquet".format(product_pair)
    print(os.path.dirname(os.path.abspath( __file__ )))
    print("[INFO] archive_path = {}".format(archive_path))

    archive_file = Path(archive_path)
    if (archive_file.is_file()):
        raise Exception("Archive File already exists at {} ! Manually remove to proceed!".format(archive_path))
    
    market_data.to_parquet(path=archive_path, compression='brotli', index=True)
    

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
    cdp_api_key = utils.load_coinbase_api_key()
    file_name = 'products_{}.json'.format(datetime.now().date())
    dump_file = Path('..\\data\\' + file_name)
    
    client = RESTClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'])
    products = client.get_products()
    print("[INFO] Sourced {} products".format(products['num_products']))

    if (save_to_json):
        file_name = 'products_{}.json'.format(datetime.now().date())
        dump_file = Path('\\..\\data\\' + file_name)
        
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
    
    dump_file = Path('..\\data\\' + file_name)
    if (not dump_file.is_file()):
        raise Exception("invalid archive file: {}".format(file_name))

    with open(dump_file, 'r') as fp:    
        data = json.load(fp)
        print("[INFO] Loaded {} products from {}".format(len(data), dump_file))

    return data


def get_ticks_as_merged_df(symbols: set[str], columns_to_drop: list[str]) -> pd.DataFrame:
    """
    TODO: decide if methods from mkt_data return standard lib structures or ok to return DFs
    
    columns_to_drop: list[str]
        columns to be dropped from the individual DataFrames
    """
    
    merged_df = pd.DataFrame({'start' : []})

    for sym in symbols:

        ticks = get_candles('{}-USD'.format(sym))
        df = utils.convert_tick_data_to_dataframe(ticks, columns_to_drop)
        df = df.add_suffix('_' + sym)
        df = df.rename({'start_' + sym : 'start'}, axis=1) # cleaner than a manual rename of all cols

        if (merged_df.empty):
            merged_df = merged_df.merge(df, how='right', on='start')
        else:
            merged_df = merged_df.merge(df, on='start') # no suffixes as we should never clash

    return merged_df


if __name__ == '__main__':
    # ticks = get_candles('BTC-USD')
    # df = utils.convert_tick_data_to_dataframe(ticks=ticks, columns_to_drop=[])

    # archive_candles(df, 'BTC-USD')
    loaded = get_archived_candles('BTC-USD')
    print(loaded)
    # print(df.compare(loaded))