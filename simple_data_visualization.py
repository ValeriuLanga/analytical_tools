import pandas as pd
import numpy as np

import plotly.express as px

from dash import Dash, html, dcc, callback, Output, Input

import market_data
import utils

@callback(
        Output('graph-content', 'figure'),
        Input('dropdown-selection', 'value')
    )
def update_graph(value: str):
    cols = []
    for sym in symbols:
        cols.append(value + '_' + sym)

    print('[INFO] showing data for {}'.format(cols))
    return px.line(merged_df, x='start', y=cols)


def merge_symbols_data(symbols: set[str]) -> pd.DataFrame:
    merged_df = pd.DataFrame({'start' : []})

    for sym in symbols:

        ticks = market_data.get_candles('{}-USD'.format(sym))
        df = utils.convert_tick_data_to_dataframe(ticks)
        df = df.add_suffix('_' + sym)
        df = df.rename({'start_' + sym : 'start'}, axis=1) # cleaner than a manual rename of all cols

        if (merged_df.empty):
            merged_df = merged_df.merge(df, how='right', on='start')
        else:
            merged_df = merged_df.merge(df, on='start') # no suffixes as we should never clash

    return merged_df


symbols = set(['BTC', 'SOL', 'AVAX'])
merged_df = merge_symbols_data(symbols)
# print(merged_df.head())

# run the app
app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='SOL/BTC - USD levels', style={'textAlign':'center'}),
    dcc.Dropdown(options=['low', 'high', 'open', 'close', 'volume'],
                  value='close', 
                  id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

app.run(debug=True)