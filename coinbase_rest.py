import pandas as pd

from json import dumps
from coinbase.rest import RESTClient

import plotly.express as px

from dash import Dash, html, dcc, callback, Output, Input

import market_data
import utils

@callback(
        Output('graph-content', 'figure'),
        Input('dropdown-selection', 'value')    # TODO: fix this, won't work w 2 args
    )
def update_graph(value: str):
    # selection = btc_df[value]
    # print(selection)
    cols = [value + '_btc', value + '_sol']
    return px.line(unified_df, x='start', y=cols)


if __name__ == '__main__':
    # BTC
    ticks_btc = market_data.get_candles('AVAX-USD')
    btc_df = utils.convert_tick_data_to_dataframe(ticks=ticks_btc)

    # SOL
    ticks_sol = market_data.get_candles('SOL-USD')
    sol_df = utils.convert_tick_data_to_dataframe(ticks=ticks_sol)

    unified_df = btc_df.merge(sol_df, on='start', suffixes=['_btc', '_sol'])

    # fig = px.line(btc_df, x='start', y='close')
    # fig.show()

    app = Dash(__name__)
    app.layout = html.Div([
        html.H1(children='SOL/BTC - USD levels', style={'textAlign':'center'}),
        dcc.Dropdown(options=['low', 'high', 'open', 'close', 'volume'], value='close', id='dropdown-selection'),
        dcc.Graph(id='graph-content')
    ])

    app.run(debug=True)

    # # all_products = market_data.get_products(save_to_json=True)
    # all_products = market_data.get_archived_product_data(date='2024-07-14')

    # # product id
    # for product in all_products:
    #      if (product['quote_display_symbol'] == 'USD' and (
    #             'PAAL' in product['base_name'] 
    #             or '0x0' in product['base_name'])):
    #           print(product)