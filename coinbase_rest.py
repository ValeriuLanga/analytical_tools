import pandas as pd

from json import dumps
from coinbase.rest import RESTClient

import plotly.express as px

from dash import Dash, html, dcc, callback, Output, Input

import market_data

@callback(
        Output('graph-content', 'figure'),
        Input('dropdown-selection', 'value')    # TODO: fix this, won't work w 2 args
    )
def update_graph(value: str, unified_df):
        # selection = btc_df[value]
        # print(selection)
        cols = [value + '_btc', value + '_sol']
        return px.line(unified_df, x='start', y=cols)

def format_tick_data(ticks: dict) -> pd.DataFrame:
    df = pd.DataFrame(ticks['candles'])
    
    # TODO: more params to deal w time
    df['start'] = pd.to_datetime(df['start'], unit='s') # convert back to 'normal' time
    df = df.astype({'low': 'float',
                'high': 'float',
                'open': 'float',
                'close': 'float',
                'volume': 'float'})

    return df

if __name__ == '__main__':
    # # BTC
    # ticks_btc = market_data.get_candles('BTC-USD')
    # btc_df = format_tick_data(ticks=ticks_btc)

    # # SOL
    # ticks_sol = market_data.get_candles('SOL-USD')
    # sol_df = format_tick_data(ticks=ticks_sol)

    # unified_df = btc_df.merge(sol_df, on='start', suffixes=['_btc', '_sol'])

    # fig = px.line(btc_df, x='start', y='close')
    # fig.show()

    # app = Dash(__name__)
    # app.layout = html.Div([
    #     html.H1(children='SOL/BTC - USD levels', style={'textAlign':'center'}),
    #     dcc.Dropdown(options=['low', 'high', 'open', 'close', 'volume'], value='close', id='dropdown-selection'),
    #     dcc.Graph(id='graph-content')
    # ])

    # app.run(debug=True)

    all_products = market_data.get_products(True)

    # product id
    for product in all_products:
         if (product['quote_display_symbol'] == 'USD' and (
                'PAAL' in product['base_name'] 
                or '0x0' in product['base_name'])):
              print(product)