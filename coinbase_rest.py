import json
import datetime

import pandas as pd

from json import dumps
from coinbase.rest import RESTClient

import plotly.express as px

from dash import Dash, html, dcc, callback, Output, Input

with open('conf\\cdp_api_key.json') as file: 
    cdp_api_key = json.load(file)

client = RESTClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'])
# print(dumps(client.get_product_book(product_id='BTC-USD'), indent=2))

# start_date = datetime.datetime.strptime('2024-07-01', "%Y-%m-%d")
start_date = datetime.datetime.strptime('2024-07-10', "%Y-%m-%d")
print(start_date.timestamp())
end_date = datetime.datetime.strptime('2024-07-13', "%Y-%m-%d")
print(end_date.timestamp())


ticks_btc = client.get_candles(product_id='BTC-USD', start=int(start_date.timestamp()), end=int(end_date.timestamp()), granularity='ONE_HOUR')

client = RESTClient(api_key=cdp_api_key['name'], api_secret=cdp_api_key['privateKey'])
ticks_sol = client.get_candles(product_id='SOL-USD', start=int(start_date.timestamp()), end=int(end_date.timestamp()), granularity='ONE_HOUR')
# print(dumps(ticks, indent=2))

# btc_df = pd.read_json(ticks['candles'], convert_axes=True)
btc_df = pd.DataFrame(ticks_btc['candles'])
btc_df['start'] = pd.to_datetime(btc_df['start'], unit='s') # convert back to 'normal' time
btc_df = btc_df.astype({'low': 'float',
               'high': 'float',
               'open': 'float',
               'close': 'float',
               'volume': 'float'})

## SOLANA
sol_df = pd.DataFrame(ticks_sol['candles'])
sol_df['start'] = pd.to_datetime(sol_df['start'], unit='s') # convert back to 'normal' time
sol_df = sol_df.astype({'low': 'float',
               'high': 'float',
               'open': 'float',
               'close': 'float',
               'volume': 'float'})

unified_df = btc_df.merge(sol_df, on='start', suffixes=['_btc', '_sol'])
#################### show the data

# fig = px.line(btc_df, x='start', y='close')
# fig.show()

app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='SOL/BTC - USD levels', style={'textAlign':'center'}),
    dcc.Dropdown(options=['low', 'high', 'open', 'close', 'volume'], value='close', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection','value')
)

def update_graph(value: str):
    # selection = btc_df[value]
    # print(selection)
    cols = [value + '_btc', value + '_sol']
    return px.line(unified_df, x='start', y=cols)


if __name__ == '__main__':
    app.run(debug=True)

print(datetime.datetime.fromtimestamp(1720566000))
print(datetime.datetime.fromtimestamp(1720569600))