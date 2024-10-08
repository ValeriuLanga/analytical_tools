import json
import os
import pandas as pd
import numpy as np

from data_sourcing import utils
import sys

from pathlib import Path
from coinbase.rest import RESTClient
from datetime import datetime


def get_candles(product_pair: str, start_date: int, end_date: int, retry_count=6) -> dict:
    """
    Args:
        start_date: in UNIX time
        end_date: in UNIX time
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
                print("[EROR] Failed to get market data!")
                return {}   # TODO: decide on approach for market_data methods - throw, empty, err code
                # raise Exception("Failed to load market data candles! Exceeded retry count!")
            
            client = RESTClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'])

            ticks = client.get_candles(
                    product_id=product_pair,
                    start=start_date,
                    end=end_date,
                    granularity='SIX_HOUR'
                    )
            return ticks
        except Exception as e: 
            retry_count -= 1
            print("[WARN] Failed to get market data for {}! Retries left {}!\n{}".format
                  (product_pair, retry_count, e))


def load_archived_market_data(product_pair: str, start_date: str, end_date: str) -> pd.DataFrame:
    archive_path = "data\\{}_{}_to_{}.parquet".format(product_pair, start_date, end_date)
    print("[INFO] archive_path = {}".format(archive_path))

    archive_file = Path(archive_path)
    if (not archive_file.is_file()):
        raise Exception("Archive File does NOT exist at {} ! Archive the data before attempting to load!"
                        .format(archive_path))
    
    return pd.read_parquet(archive_path)


def archive_market_data(market_data: pd.DataFrame, product_pair: str, start_date: str, end_date: str) -> None:
    """
    Args:
        market_data: DataFrame

        product_pair: str
            crypto_id-fiat_ccy pair; see get_products().
    """
     
    archive_path = "data\\{}_{}_to_{}.parquet".format(product_pair, start_date, end_date)
    print(os.path.dirname(os.path.abspath( __file__ )))
    print("[INFO] archive_path = {}".format(archive_path))

    archive_file = Path(archive_path)
    if (archive_file.is_file()):
        raise Exception("Archive File already exists at {} ! Manually remove to proceed!".format(archive_path))
    
    market_data.to_parquet(path=archive_path, compression='brotli', index=True)
    

def get_products(save_to_json=False) -> list[dict]:
    """
    """
    cdp_api_key = utils.load_coinbase_api_key()
    file_name = 'products_{}.json'.format(datetime.now().date())
    dump_file = Path('..\\data\\' + file_name)
    
    client = RESTClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'])
    products = client.get_products()
    print("[INFO] Sourced {} products".format(products['num_products']))

    if (save_to_json):
        # TODO: move to parquet
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
    TODO: move to parquet
    '''

    file_name = 'products_{}.json'.format(date)
    
    dump_file = Path('..\\data\\' + file_name)
    if (not dump_file.is_file()):
        raise Exception("invalid archive file: {}".format(file_name))

    with open(dump_file, 'r') as fp:    
        data = json.load(fp)
        print("[INFO] Loaded {} products from {}".format(len(data), dump_file))

    return data


def get_ticks_as_merged_df(symbols: set[str], start_date: str, end_date: str, columns_to_drop: list[str]) -> pd.DataFrame:
    """
    TODO: decide if methods from mkt_data return standard lib structures or ok to return DFs
    
    columns_to_drop: list[str]
        columns to be dropped from the individual DataFrames
    """
    
    merged_df = pd.DataFrame({'start' : []})

    for sym in symbols:
        # TODO: change prod pair to tuple; abstract away some of the details
        mkt_data_pair = '{}-USD'.format(sym)

        df = get_historical_market_data(mkt_data_pair, start_date, end_date, 'SIX_HOUR')
        df = utils.normalize_crypto_market_data(df, columns_to_drop)
        df = df.add_suffix('_' + sym)   # this will also rename the 'start' column which is the time
        df = df.rename({'start_' + sym : 'start'}, axis=1) # single time for all MD ticks - rename back
        
        if (merged_df.empty):
            merged_df = merged_df.merge(df, how='right', on='start')
        else:
            merged_df = merged_df.merge(df, on='start') # no suffixes as we should never clash

    return merged_df


def get_historical_market_data(symbol: str, start_date: str, end_date: str, time_unit: str) -> pd.DataFrame:
    """
    """
    # TODO: add all possible mappings; see coinbase api for values
    units_per_day = {'SIX_HOUR' : 4}

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    days_between = abs(end_date - start_date)

    request_number = int(days_between.days * units_per_day[time_unit] / 300) + 1
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # we can get max 300 values in one REST call - so chunk it 
    intervals = np.array_split(dates, request_number)

    concatenated = pd.DataFrame()
    for interval in intervals:
        print("[INFO] Querying {} market data for interval [{} - {}]".format(symbol, interval[0], interval[-1]))
        market_data = get_candles(product_pair=symbol, 
                                  start_date=(interval[0] - pd.Timestamp('1970-01-01')) // pd.Timedelta('1s'), 
                                  end_date=(interval[-1] - pd.Timestamp('1970-01-01')) // pd.Timedelta('1s')
                                  )
        
        df = utils.convert_tick_data_to_dataframe(market_data, [], False)
        concatenated = pd.concat([df, concatenated])

    # archive_market_data(concatenated, symbol, start_date=start_date.date(), end_date=end_date.date())
    # print(concatenated)
    return concatenated