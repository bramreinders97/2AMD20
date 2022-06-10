from dash import html, dcc
from dash import Dash
from dash.dependencies import Input, Output
import geopandas as gpd
import plotly.express as px
import json
from pandas import read_pickle
import plotly.express as px
import pandas as pd

import json
from pandas import read_pickle
import plotly.express as px
import shapefile
import pandas as pd


def load_shapefile():
    geojson_data = gpd.read_file("new.json")
    geojson_data = geojson_data.to_crs(4326).__geo_interface__
    return geojson_data




def load_json():

    geojson_data = shapefile.Reader("../../gemeente_lines/gemeente_2020_v2.shp").__geo_interface__
    return geojson_data


def load_dataset(path):
    """
    Loads a dataset in.
    :param path: path to dataset.
    :return: Unpickled dataset.
    """
    data = read_pickle(path)
    return data

def make_choropleth(geojson, dataframe):

    idx = dataframe[(dataframe['RegioS'] != "GM0363")].index
    dataframe.drop(idx, inplace=True)
    print(dataframe)

    df = dataframe
    df.astype({"RegioS": str})
    geojson = geojson

    fig = px.choropleth_mapbox(df,
                               geojson=geojson,
                               color="GemiddeldeWoningwaarde_4",
                               locations="RegioS",
                               featureidkey="properties.statcode",
                               range_color=[min(df['GemiddeldeWoningwaarde_4']), max(df['GemiddeldeWoningwaarde_4'])],  
                               zoom=9,
                               center={"lat": 52.370216, "lon": 4.895168},
                               mapbox_style="carto-positron",
                               opacity=0.5)

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_geos(fitbounds="locations", visible=False)

    print("Preparing to show figure: ")
    # fig.show()
    return fig


def main(fig):
    app = Dash(__name__)
    app.title = "Knowledge Engineering Visualization"
    # fig = px.choropleth_mapbox(data_frame = load_shapefile(), featureidkey = "GM_CODE", )
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
    # j_file = load_json()
    j_file = load_shapefile()
    dataset = load_dataset("../../cleanedDFs/prices.pkl")
    figure = make_choropleth(j_file, dataset)
    main(figure)
    #figure.show()
    #main(figure)
