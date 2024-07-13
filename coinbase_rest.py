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


ticks = client.get_candles(product_id='BTC-USD', start=int(start_date.timestamp()), end=int(end_date.timestamp()), granularity='ONE_HOUR')
# print(dumps(ticks, indent=2))

# btc_df = pd.read_json(ticks['candles'], convert_axes=True)
btc_df = pd.DataFrame(ticks['candles'])

btc_df['start'] = pd.to_datetime(btc_df['start'], unit='s') # convert back to 'normal' time
# btc_df = btc_df.set_index('start')

# print(btc_df)
# print(btc_df.dtypes)
btc_df = btc_df.astype({'low': 'float',
               'high': 'float',
               'open': 'float',
               'close': 'float',
               'volume': 'float'})
# print(btc_df.dtypes)
#################### show the data

# fig = px.line(btc_df, x='start', y='close')
# fig.show()

app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='BTC-USD level', style={'textAlign':'center'}),
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
    return px.line(btc_df, x='start', y=value)


if __name__ == '__main__':
    app.run(debug=True)

print(datetime.datetime.fromtimestamp(1720566000))
print(datetime.datetime.fromtimestamp(1720569600))