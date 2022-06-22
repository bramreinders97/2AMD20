import geojson
import plotly.express as px
from dash import Dash, Input, Output, dcc, html, dash_table
from pandas import read_pickle
import pandas as pd
import re


def load_geojson():
    """
    Opens the the geojson file and returns it. The file is assumed to be in the correct coordinate system.
    :return:geojson file with municipalities.
    """

    with open("new.geojson") as f:
        geojson_data = geojson.load(f)
    return geojson_data


def make_table(df, city, factor):
    """
    Makes a small table about the city and the top 10 cities that are being moved from/to.
    :param factor: The factor chosen. (String in the format "factor_other")
    :param df: The full dataframe that has been imported. (Pandas df)
    :param city: The subject city. (A string with a capital)
    :return: A dataframe with index 0 being the subject city and the other 10 rows the top 10 cities that move to/from
             this one.
    """

    # Here we get the value for the city
    new_factor = re.sub("other", 'top_10', factor)
    city_df = df.drop(df[df.year != 2020].index)
    city_factor = city_df.iloc[0][new_factor]

    # First aggregate move data, but fuck the years
    header_agg = {'moves': 'sum',
                  factor: 'last'
                  }
    df = df.groupby(['gemeente_code', 'gemeente_naam']).agg(header_agg).reset_index()

    # Sort new dataframe on moves and keep the top 10
    df = df.sort_values(['moves'], ascending=False).head(n=10)
    df.drop('gemeente_code', axis=1, inplace=True)

    # Prepend the subject city
    df2 = pd.DataFrame({'gemeente_naam': [city], 'moves': [None], factor: [city_factor]})
    df = pd.concat([df2, df], ignore_index=True, axis=0)

    # Rename the column headers in the table
    factorB = re.sub("_other", '', factor)
    df = df.rename(columns={"moves": "Totaal verhuizingen", factor: factorB})

    return df


def aggregate_dataframe(dataframe, factor):
    """
    This function is called whenever we have more than one year selected.
    In that case we need to aggregate the data of those years.  At least for the moves it should be summed.
    It assumes that the dataframe has already thrown out the years that are not relevant.
    :param dataframe: The dataframe that needs aggregated data (Pandas df)
    :param factor: The chosen factor. (string with '_other' appended)
    :return: pandas dataframe with the moves columns aggregated.
    """

    # Aggregation options. Sum for moves and last for the chosen factor. can be changed.
    header_agg = {'moves': 'sum',
                  factor: 'last'
                  }

    # This is where the aggregation happens:
    aggregated_dataframe = dataframe.groupby(['gemeente_code', 'gemeente_naam', 'year']).agg(header_agg).reset_index()
    return aggregated_dataframe


def prepare_dataset(city, to_from, factor, years):
    """
    Loads a dataset in and filters it based on the criteria passed.
    :param city: The chosen city from the top 10. (string, with capital)
    :param to_from: Whether we want data to or from that city. (string, either To or From, with capitals)
    :param factor: Which factor we want to display. (String + '_other')
    :param years: Which years are chosen. (List)
    :return: Unpickled dataset with only relevant columns
    """

    # Construct path to dataset depending on inputs.
    base_df_path = '../../QueryDFs/'
    df_path = base_df_path + to_from + '_' + city + '.pkl'
    df = read_pickle(df_path)

    # Convert columns to new types
    df = df.astype({"gemeente_code": str, "gemeente_naam": str, "year": float, "moves": float, factor: float})

    # Save this one for the table
    full_df = df

    # Drop irrelevant years, bit convoluted but whatever
    non_years = {2016, 2017, 2018, 2019, 2020} - set(years)
    for year in non_years:
        df = df.drop(df[df.year == int(year)].index)

    # Drop irrelevant columns unless specified that we want all columns
    if factor != 'all':
        df = df[['gemeente_code', 'gemeente_naam', 'year', 'moves', factor]]

    # If the user wants more than one year, we need to aggregate the data of those years
    if len(years) > 1:
        df = aggregate_dataframe(dataframe=df, factor=factor)

    return df, full_df


def make_choropleth(geojson_file, city='Amsterdam', to_from='From', factor='prices_other', years=None, sorting=True):
    """
    Function to make the actual choropleth figure.
    Should be called on whenever the user presses an update button somewhere in the dash_app.
    :param geojson_file: A geojson file with the municipality data. (geojson)
    :param city: One of the top 10 cities. (string, with capital letter)
    :param to_from: Whether we want data to or from that city. (string, either To or From, with capitals)
    :param factor: Which factor we want to display. (String, no capital letters, format = "factor_other")
    :param years: Which years are chosen. (List of ints)
    :param sorting: A boolean, signifying whether we want to color the choropleth based on moves (True)
                    or based on the chosen factor (False).
    :return: Returns a figure.
    """

    if years is None:
        years = [2016]

    # Prepare dataset according to the chosen parameters

    df, full_df = prepare_dataset(city=city, to_from=to_from, factor=factor, years=years)

    # Decide what factor to base the choropleth colouring on. If multiple years, only show based on moves.
    if sorting or len(years) > 1:
        color = 'moves'
    else:
        color = factor

    # Make the actual choropleth
    fig = px.choropleth_mapbox(df,
                               geojson=geojson_file,
                               color=color,
                               locations="gemeente_code",
                               featureidkey="properties.statcode",
                               range_color=[min(df[color]), max(df[color])],
                               zoom=6,
                               color_continuous_scale= 'Reds',
                               hover_name=df["gemeente_naam"],
                               hover_data=["moves", factor, "year"],
                               center={"lat": 52.2130, "lon": 5.2794},
                               mapbox_style="carto-positron",
                               opacity=0.5)

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_geos(fitbounds="locations", visible=False)

    # Also make a new table
    table = make_table(full_df, city, factor)

    return fig, table


def main(geojson_file):
    """
    This is the main dash app. This thing does the whole visualization
    :param geojson_file: A geojson file with the municipality borders in standard lat, lon coordinates.
    """

    # Create dash board
    app = Dash(__name__)
    app.title = "Knowledge Engineering Visualization"
    fig, table = make_choropleth(geojson_file)
    print(table)
    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=4,
            autoexpand=True
        ), height=800
    )

    app.layout = html.Div([
        html.Div(children=[

            # Place option selectors
            html.H1('Visualization of Movement in the Netherlands'),

            html.Div([
                html.H3('Select a City'),
                dcc.Dropdown(id='city',
                             options=["Almere", "Amsterdam", "Breda", "DenHaag", "Eindhoven", "Groningen",
                                      "Nijmegen", "Rotterdam", "Tilburg", "Utrecht"], value="Amsterdam"
                             )
            ], style={'width': '18%', 'vertical-align': 'top', 'display': 'inline-block', 'margin-left': '15px'}),

            html.Div([html.H3('Movement Reason'),
                      dcc.Dropdown(id='direction',
                                   options=[{'label': nametitle, 'value': name} for nametitle, name in
                                            zip(["From", "Towards"], ["From", "To"])], value="From"
                                   )],
                     style={'width': '18%', 'vertical-align': 'top', 'display': 'inline-block', 'margin-left': '15px'}),

            html.Div([html.H3('Coloring Factor'),
                      dcc.Dropdown(id='factor',
                                   options=[{'label': nametitle, 'value': name} for nametitle, name in
                                            zip(["Housing Availability", "Average Housing Prices",
                                                 "Population Size"],
                                                ["availability_other", "prices_other", "population_other"])],
                                   value="prices_other"
                                   )],
                     style={'width': '18%', 'vertical-align': 'top', 'display': 'inline-block', 'margin-left': '15px'}),

            html.Div([html.H3('Sorting Factor'),
                      dcc.Dropdown(id='sorting',
                                   options=[{'label': nametitle, 'value': name} for nametitle, name in
                                            zip(["Sort on Movement", "Sort on Chosen Factor"],
                                                [True, False])], value=True,
                                   )],
                     style={'width': '18%', 'vertical-align': 'top', 'display': 'inline-block', 'margin-left': '15px'}),

            html.Div(
                [html.H3('Select Years'),
                 dcc.Checklist(id='year_checklist', options=[2016, 2017, 2018, 2019, 2020], inline=True,
                               value=[2016, 2017, 2018, 2019, 2020],
                               style={'margin-top': '25px'}), ],
                style={'width': '18%', 'vertical-align': 'top', 'display': 'inline-block', 'margin-left': '15px'}),


        ]),
        
        html.Div(children=[
            # Place the map
            html.H4("Map"),
            html.Div(
                [dcc.Graph(id='choropleth', figure=fig)])
        ]),
                        html.Div(children=[
            html.H4("Table"),
            html.Div([dash_table.DataTable(table.to_dict('records'), [{"name": i, "id": i} for i in table.columns], id = "datatable")])
        ]),])

    # Make callbacks to update selection
    @app.callback(
        Output(component_id='choropleth', component_property='figure'),
        Output(component_id ='datatable', component_property='data'),
        Input(component_id='city', component_property='value'),
        Input(component_id='direction', component_property='value'),
        Input(component_id='factor', component_property='value'),
        Input(component_id='sorting', component_property='value'),
        Input(component_id='year_checklist', component_property='value')
    )
    # Call make_choropleth to update the figure
    def update_figure(city, direction, factor, sorting, year_checklist):
        """
        Calls make_choropleth with the chosen variables and updates the dash app.
        """
        new_choropleth, new_table = make_choropleth(geojson_file=geojson_file, city=city, to_from=direction,
                                                    factor=factor,
                                                    years=year_checklist, sorting=sorting)
        new_choropleth.update_layout(
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=4,
                autoexpand=True
            ), height=800
        )

        

        return new_choropleth, new_table.to_dict('records')
    app.run_server(debug=False, dev_tools_ui=False)


if __name__ == '__main__':
    j_file = load_geojson()
    main(j_file)
