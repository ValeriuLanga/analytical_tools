import pandas as pd
import plotly.express as px

from dash import Dash, html, dcc, callback, Output, Input


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
print(df)

app = Dash(__name__)
app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection','value')
)

def update_graph(value: str):
    selection = df[df.country == value]
    return px.line(selection, x='year', y='pop')



if __name__ == '__main__':
    app.run(debug=True)
