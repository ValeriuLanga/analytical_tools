import json

import pandas as pd

def load_api_key() -> dict:
    with open('conf\\cdp_api_key.json') as file: 
        cdp_api_key = json.load(file)
    
    return cdp_api_key

def convert_tick_data_to_dataframe(ticks: dict) -> pd.DataFrame:
    df = pd.DataFrame(ticks['candles'])
    
    # TODO: more params to deal w time
    df['start'] = pd.to_datetime(df['start'], unit='s') # convert back to 'normal' time
    df = df.astype({'low': 'float',
                'high': 'float',
                'open': 'float',
                'close': 'float',
                'volume': 'float'})

    return df

def dump_json_array_to_disk(file_prefix: str) -> None:
    pass