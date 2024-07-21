import json
import pandas as pd

from datetime import datetime

def load_coinbase_api_key() -> dict:
    with open('conf\\cdp_api_key.json') as file: 
        cdp_api_key = json.load(file)
    
    return cdp_api_key


def load_eod_data_api_key() -> dict:
    with open('conf\\eod_data_api_key.json') as file: 
        key = json.load(file)
    
    return key


def convert_date_to_unix_time(date: str) -> int:
    converted = datetime.strptime(date, "%Y-%m-%d")
    return int(converted.timestamp())


def normalize_crypto_market_data(market_data: pd.DataFrame, columns_to_drop: list[str]) -> pd.DataFrame:
    market_data = market_data.astype({
                'start': 'float',
                'low': 'float',
                'high': 'float',
                'open': 'float',
                'close': 'float',
                'volume': 'float'})

    # TODO: more params to deal w time
    market_data['start'] = pd.to_datetime(market_data['start'], unit='s') # convert back to 'normal' time
    
    if (len(columns_to_drop) > 0):
        # print("[INFO] Dropping {}".format(columns_to_drop))
        market_data = market_data.drop(labels=columns_to_drop, axis=1)

    return market_data


def convert_tick_data_to_dataframe(ticks: dict, columns_to_drop: list[str], normalize: bool = False) -> pd.DataFrame:
    df = pd.DataFrame(ticks['candles'])
    
    if (normalize):
        return normalize_crypto_market_data(df, columns_to_drop)
    return df

def dump_json_array_to_disk(file_prefix: str) -> None:
    pass
