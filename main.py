import os
import datetime
import pandas as pd
from dotenv import dotenv_values
import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc


GLOBAL_CONFIG = dotenv_values(".env")
GLOBAL_DECKS_DF = pd.read_csv(os.path.join(GLOBAL_CONFIG['DATA_DIR'], 'decks.csv'), sep=';')



# get random deck for today
def get_dotd():
    d = datetime.date.today()
    d0 = datetime.date(1970, 1, 1)
    delta = (d - d0).days
    dotd = GLOBAL_DECKS_DF.iloc[delta%GLOBAL_DECKS_DF.shape[0]]
    return dotd


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'])

dotd = get_dotd()

app.layout = html.Div(children=[
    dbc.Row(
        dbc.Col([

            html.Div([
                
                html.Span('Budget', className='pro'),
                
                html.Img(src="https://cards.scryfall.io/art_crop/front/a/0/a062a004-984e-4b62-960c-af7288f7a3e9.jpg", width=200, className='round'),
                
                html.H3('{}'.format(dotd['name'])),
                
                html.Span([
                    html.Img(src="assets/w.png", width=15),
                    html.Img(src="assets/b.png", width=15),
                    html.Img(src="assets/r.png", width=15),
                ]),
                
                html.P('70€ Isshin On-Attack Value'),
                
                html.Div([
                    html.Button('Get Deck', id='btn-get-deck', n_clicks=0, className='primary ghost'),
                    html.Button('Deck of the Day', id='btn-deck-dotd', className='primary ghost'),
                ], className='buttons'),

                html.Div(
                    dbc.Row([
                        dbc.Col(html.I(className='fa fa-level-down', style={'padding-top': '5px'}, id='icon-filters-close'), width=4),
                        dbc.Col(html.H6('Filters'), width=8),
                    ]), style={'margin-top': '10px'}
                ),

                dbc.Collapse([

                    dbc.Row([
                        dbc.Col(html.Label('Combo'), width=4),
                        dbc.Col(daq.ToggleSwitch(id='toggle-has-combo', value=True), width=8)
                    ]),


                    dbc.Row([
                        dbc.Col(html.Label('Colors'), width=4),
                        dbc.Col(dcc.RangeSlider(0, 5, 1, value=[0, 5], id='range-slider-colors'), width=8)
                    ]),

                    dbc.Row([
                        dbc.Col(html.Label('Budget'), width=4),
                        dbc.Col(daq.ToggleSwitch(id='toggle-is-budget', value=True), width=8)
                    ]),

                    dbc.Row([
                        dbc.Col(html.Label('Colors'), width=4),
                        dbc.Col(
                            html.Span([
                                html.Img(src="assets/w.png", width=25, id='color-w'),
                                html.Img(src="assets/u.png", width=25, id='color-u'),
                                html.Img(src="assets/b.png", width=25, id='color-b'),
                                html.Img(src="assets/r.png", width=25, id='color-r'),
                                html.Img(src="assets/g.png", width=25, id='color-g'),
                            ]),
                        )
                    ]),

                ], id='collapse-deck-filters', is_open=False),

                html.Div([
                    html.H6('Tags'),
                    html.Ul([
                        html.Li('Combat'),
                        html.Li('Budget'),
                        html.Li('Mardu'),
                        html.Li('No Combo'),
                        html.Li('On Attack'),
                        html.Li('Value')
                    ])
                ], className='skills'),

            ], className='card-container')
        ])
    ),
])


@app.callback(
    [Output("collapse-deck-filters", "is_open"),
    Output("icon-filters-close", 'className')],
    Input("icon-filters-close", "n_clicks"),
    prevent_initial_call=True
)
def collapse_filters(n_clicks):
    if n_clicks%2==1:
        return True, 'fa fa-level-up'
    else:
        return False, 'fa fa-level-down'



if __name__=='__main__':
    app.run_server(debug=True)
