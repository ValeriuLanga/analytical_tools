import json

import pandas as pd

def load_coinbase_api_key() -> dict:
    with open('conf\\cdp_api_key.json') as file: 
        cdp_api_key = json.load(file)
    
    return cdp_api_key

def load_eod_data_api_key() -> dict:
    with open('conf\\eod_data_api_key.json') as file: 
        key = json.load(file)
    
    return key

def convert_tick_data_to_dataframe(ticks: dict, columns_to_drop: list[str]) -> pd.DataFrame:
    df = pd.DataFrame(ticks['candles'])
    
    df = df.astype({'start': 'float',
                'low': 'float',
                'high': 'float',
                'open': 'float',
                'close': 'float',
                'volume': 'float'})

    # TODO: more params to deal w time
    df['start'] = pd.to_datetime(df['start'], unit='s') # convert back to 'normal' time
    
    if (len(columns_to_drop) > 0):
        # print("[INFO] Dropping {}".format(columns_to_drop))
        df = df.drop(labels=columns_to_drop, axis=1)

    return df

def dump_json_array_to_disk(file_prefix: str) -> None:
    pass
