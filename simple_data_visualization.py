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

    fig = px.line(merged_df, x='start', y=cols)
    fig.update_xaxes(rangeslider_visible=True)

    return fig


symbols = set(['LTC', 'SOL', 'AVAX'])
merged_df = market_data.get_ticks_as_merged_df(symbols)
# print(merged_df.head())

# run the app
app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='Price and volume information', style={'textAlign':'center'}),
    dcc.Dropdown(options=['low', 'high', 'open', 'close', 'volume'],
                  value='close', 
                  id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

app.run(debug=True)