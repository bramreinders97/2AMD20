from dash import html, dcc
from dash import Dash
from dash.dependencies import Input, Output
import geopandas as gpd


def load_shapefile():
    path = "/gemeente_lines/gemeente_2020_v2.shp"
    shapefile = gpd.read_file(path)
    return shapefile


def main():
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
            [dcc.Checklist(id='year-checklist', options=[2016, 2017, 2018, 2019, 2020], value=2016, inline=True)])])

    # Callbacks maken dat hij update op selectie

    app.run_server(debug=False, dev_tools_ui=False)


if __name__ == '__main__':
    main()
    load_shapefile()