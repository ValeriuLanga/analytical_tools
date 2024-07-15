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
        # TODO: add a switch on what types of data we want to see
        cols = ['ln_returns_btc', 'ln_returns_sol', 'ln_return_corr']
        # cols = [value + '_btc', value + '_sol']

        print("[INFO] updating graph with data from {}".format(cols))
        return px.line(unified_df, x='start', y=cols)


# load BTC
ticks_btc = market_data.get_candles('BTC-USD')
btc_df = utils.convert_tick_data_to_dataframe(ticks=ticks_btc)

# load SOL
ticks_sol = market_data.get_candles('SOL-USD')
sol_df = utils.convert_tick_data_to_dataframe(ticks=ticks_sol)

# bring both into one df
unified_df = btc_df.merge(sol_df, on='start', suffixes=['_btc', '_sol'])

# compute ln returns per time interval (see market_data.get_candles())
unified_df['ln_returns_btc'] = np.log(unified_df['close_btc'] / unified_df['close_btc'].shift(1))
unified_df['ln_returns_sol'] = np.log(unified_df['close_sol'] / unified_df['close_sol'].shift(1))

# high level correlation stats
print('[INFO] BTC <> SOL correlation', unified_df.corr()['ln_returns_sol']['ln_returns_btc'])
print('[INFO] BTC <> SOL leading / lagging correlation', 
      unified_df['ln_returns_btc'].corr(unified_df['ln_returns_sol'].shift(2)))

# let's have a look at a rolling correlation 
unified_df['ln_return_corr'] = unified_df['ln_returns_btc'].rolling(3).corr(unified_df['ln_returns_sol'].shift(2))
print('[INFO] Rolling BTC <> SOL correlation', unified_df['ln_return_corr'])


# run the app
app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='SOL/BTC - USD levels', style={'textAlign':'center'}),
    dcc.Dropdown(options=['low', 'high', 'open', 'close', 'volume', 'ln_returns'],
                  value='close', 
                  id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

app.run(debug=True)
