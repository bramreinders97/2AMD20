from dash import html, dcc
from dash import Dash
from dash.dependencies import Input, Output
import json
from pandas import read_pickle
import plotly.express as px


def load_json():
    path = "extracted.txt"
    j_file = json.load(open(path))
    return j_file


def load_dataset(path):
    """
    Loads a dataset in.
    :param path: path to dataset.
    :return: Unpickled dataset.
    """
    data = read_pickle(path)
    return data


def compress_json(file):
    """
    This one might be needed if the visualization is too slow.
    Will round down the coordinates of the municipalities in te json file
    :param file: A json file
    :return: A json file with the coordinates rounded up/down.
    """
    pass


def make_choropleth(geojson, dataframe):
    print("yo")
    df = dataframe
    geojson = geojson

    fig = px.choropleth_mapbox(
        df, geojson=geojson, color="BevolkingOp1Januari_1",
        locations="RegioS", featureidkey="properties.GM_CODE",
        range_color=[0, 6500], zoom=5)
    print("yo2")
    return fig


def main(fig):
    app = Dash(__name__)
    app.title = "Knowledge Engineering Visualization"
    app.layout = html.Div([
        html.H1('Visualization of Movement in the Netherlands'),
        html.H3('Select the City'),
        # Al die zips moeten ingevuld worden en gelinkt aan onze daadwerklijke data
        html.Div([
            dcc.Dropdown(id='city',
                         options=[{'label': nametitle, 'value': name} for nametitle, name in
                                  zip([1, 2], ["Adam", "Rdam"])],
                         value=1)
        ], style={'width': '20%'}),
        html.H3('Select the Direction'),
        html.Div([dcc.Dropdown(id='direction',
                               options=[{'label': nametitle, 'value': name} for nametitle, name in
                                        zip([1, 2], ["van", "naar"])],
                               value=1)], style={'width': '20%'}),
        html.H3('Select the factor'),
        html.Div([dcc.Dropdown(id='factor',
                               options=[{'label': nametitle, 'value': name} for nametitle, name in
                                        zip([1, 2], ["van", "naar"])],
                               value=1)], style={'width': '20%'}),
        html.H3('Select the sorting'),
        html.Div([dcc.Dropdown(id='sorting',
                               options=[{'label': nametitle, 'value': name} for nametitle, name in
                                        zip([1, 2], ["van", "naar"])],
                               value=1)], style={'width': '20%'}),
        html.H3('Select the years of interest'),
        html.Div(
            [dcc.Checklist(id='year-checklist', options=[2016, 2017, 2018, 2019, 2020], value=2016, inline=True)]),

        html.H4("BigMap"),
        html.Div(
            [dcc.Graph(id='example-graph-1', figure=fig)])])

    # Callbacks maken dat hij update op selectie

    app.run_server(debug=False, dev_tools_ui=False)


if __name__ == '__main__':
    j_file = load_json()
    dataset = load_dataset("population.pkl")
    figure = make_choropleth(j_file, dataset)
    main(figure)
