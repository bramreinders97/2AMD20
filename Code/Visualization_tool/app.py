import geojson
import plotly.express as px
from dash import Dash, dcc, html
from pandas import read_pickle


def load_geojson():
    """
    Opens the the geojson file and returns it. The file is assumed to be in the correct coordinate system.
    :return:geojson file with municipalities.
    """

    with open("new.geojson") as f:
        geojson_data = geojson.load(f)
    return geojson_data


def aggregate_dataframe(dataframe, factor):
    """
    This function is called whenever we have more than one year selected.
    In that case we need to aggregate the data of those years.  At least for the moves it should be summed.
    It assumes that the dataframe has already thrown out the year that are not relevant.
    :param dataframe: The dataframe that needs aggregated data (Pandas df)
    :param factor: The chosen factor. (string with '_other' appended)
    :return: pandas dataframe with the moves columns aggregated.
    """
    # TODO: How exactly do we want to aggregate the other columns. I believe that the latest variable is actually fine.
    #  Maybe we want a difference score? it can be adapted in header_agg

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

    # Drop irrelevant columns unless specified that we want all columns
    if factor != 'all':
        df = df[['gemeente_code', 'gemeente_naam', 'year', 'moves', factor]]

    # Drop irrelevant years
    df = df.loc[(df['year'].isin(years))]

    # If the user wants more than one year, we need to aggregate the data of those years
    if len(years) > 1:
        df = aggregate_dataframe(dataframe=df, factor=factor)

    return df


def make_choropleth(geojson_file, city='Amsterdam', to_from='To', factor='prices', years=None, sorting=True):
    """
    Function to make the actual choropleth figure.
    Should be called on whenever the user presses an update button somewhere in the dash_app.
    :param geojson_file: A geojson file with the municipality data. (geojson)
    :param city: One of the top 10 cities. (string, with capital letter)
    :param to_from: Whether we want data to or from that city. (string, either To or From, with capitals)
    :param factor: Which factor we want to display. (String, no capital letters)
    :param years: Which years are chosen. (List of ints)
    :param sorting: A boolean, signifying whether we want to color the choropleth based on moves (True)
                    or based on the chosen factor (False).
    :return: Returns a figure.
    """

    # This is just a default parameter, because i don't know how dash updates itself.
    if years is None:
        years = [2016]

    # I believe bram constructed the column name to be this format, so we need to change factor
    factor = factor + '_other'

    # Prepare dataset according to the chosen parameters
    df = prepare_dataset(city=city, to_from=to_from, factor=factor, years=years)

    # Decide what factor to base the choropleth colouring on
    if sorting:
        color = 'moves'
    else:
        color = factor + '_other'

    # Make the actual choropleth
    fig = px.choropleth_mapbox(df,
                               geojson=geojson_file,
                               color=color,
                               locations="RegioS",
                               featureidkey="properties.statcode",
                               range_color=[min(df[factor]), max(df[factor])],
                               zoom=9,
                               center={"lat": 52.370216, "lon": 4.895168},
                               mapbox_style="carto-positron",
                               opacity=0.5)

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_geos(fitbounds="locations", visible=False)

    return fig


def main(geojson_file):

    # Initialize a figure? I am not sure if this is needed
    fig = make_choropleth(geojson_file=geojson_file)

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

    # Make callbacks to update selection

    app.run_server(debug=False, dev_tools_ui=False)
    # TODO: Hier zouden die callbacks moeten plaatsvinden om make_choropleth aan te roepen. Geen idee hoe.
    #  Het format om make_choropleth aan te roepen is the vinden in de desbetreffende docstring.




if __name__ == '__main__':
    j_file = load_geojson()
    main(j_file)