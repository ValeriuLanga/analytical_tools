import pandas as pd
import numpy as np

import plotly.express as px

from data_sourcing import crypto_market_data, utils

def add_ln_returns_to_df(df: pd.DataFrame, symbol: str):
    """
    """

    price_col_name = 'close_' + symbol
    ln_returns_col_name = 'ln_returns_' + symbol
    
    df[ln_returns_col_name] = np.log(df[price_col_name] / df[price_col_name].shift(1))


#######
symbols = set(['BTC', 'SOL', 'AVAX', 'AXS', 'ARKM', 'ILV'])
unified_df = crypto_market_data.get_ticks_as_merged_df(
    symbols=symbols, 
    start_date='2024-05-13',
    end_date='2024-07-13',
    columns_to_drop=['low', 'high', 'open', 'volume']
    )

for sym in symbols:
    add_ln_returns_to_df(unified_df, sym)

# drop close pxs
unified_df = unified_df.drop(labels=(x for x in unified_df.columns if x.startswith('close')), axis=1)
unified_df = unified_df.drop(columns=['start'])

# overall ln return correlation
correlation_matrix = unified_df.corr()

# let's print some stats
for sym in symbols:
    col_name = 'ln_returns_' + sym
    sym_corr = correlation_matrix[col_name] # note that this is a series, not a df

    highest_corr_name = sym_corr[sym_corr < 1].idxmax()
    print("[STAT] Highest correlation for {} - {} = {}".format(
        sym, 
        sym_corr[sym_corr < 1].idxmax(), 
        sym_corr[highest_corr_name])) # ofc corr (sym, sym) = 1
    
    lowest_corr_name = sym_corr.idxmin() 
    print("[STAT] Lowest correlation for {} - {} = {}".format(
        sym, 
        lowest_corr_name,
        sym_corr[lowest_corr_name]))

# finally let's look at the matrix as a heat map
fig = px.imshow(correlation_matrix, text_auto=True)
fig.show()
