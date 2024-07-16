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
    cols = ['ln_returns_BTC', 'ln_returns_SOL', 'ln_return_corr']
    # cols = [value + '_btc', value + '_sol']

    print("[INFO] updating graph with data from {}".format(cols))
    fig = px.line(unified_df, x='start', y=cols)
    fig.update_xaxes(rangeslider_visible=True)

    return fig

def add_ln_returns_to_df(df: pd.DataFrame, symbol: str):
    """
    """

    price_col_name = 'close_' + symbol
    ln_returns_col_name = 'ln_returns_' + symbol
    
    df[ln_returns_col_name] = np.log(df[price_col_name] / df[price_col_name].shift(1))


#######
symbols = set(['BTC', 'SOL', 'AVAX', 'AXS', 'ARKM', 'ILV'])
unified_df = market_data.get_ticks_as_merged_df(symbols=symbols, columns_to_drop=['low', 'high', 'open', 'volume'])

for sym in symbols:
    add_ln_returns_to_df(unified_df, sym)

# drop close pxs
unified_df = unified_df.drop(labels=(x for x in unified_df.columns if x.startswith('close')), axis=1)
unified_df = unified_df.drop(columns=['start'])

# overall ln return correlation
correlation_matrix = unified_df.corr()
# print(correlation_matrix)

fig = px.imshow(correlation_matrix, text_auto=True)

fig.show()


# # high level correlation stats
# print('[INFO] Overall correlation', )
# print('[INFO] BTC <> SOL leading / lagging correlation', 
#       unified_df['ln_returns_BTC'].corr(unified_df['ln_returns_SOL'].shift(2)))

# # let's have a look at a rolling correlation 
# unified_df['ln_return_corr'] = unified_df['ln_returns_BTC'].rolling(3).corr(unified_df['ln_returns_SOL'].shift(2))
# print('[INFO] Rolling BTC <> SOL correlation', unified_df['ln_return_corr'])

# # run the app
# app = Dash(__name__)
# app.layout = html.Div([
#     html.H1(children='SOL/BTC - USD levels', style={'textAlign':'center'}),
#     dcc.Dropdown(options=['low', 'high', 'open', 'close', 'volume', 'ln_returns'],
#                   value='close', 
#                   id='dropdown-selection'),
#     dcc.Graph(id='graph-content')
# ])

# app.run(debug=True)