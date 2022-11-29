import os
import random
import datetime
import pandas as pd
from dotenv import dotenv_values
import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
from requests import get
from json import loads



GLOBAL_DECKS_DF = pd.read_csv(os.path.join('assets/decks.csv'), sep=';')
GLOBAL_LAST_IDX = None





app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'])

app.layout = html.Div(children=[
    dbc.Row(
        dbc.Col([

            html.Div([
                
                html.Span('Budget', className='pro', id='span-deck-budget'),
                
                html.Img(src='', width=200, id='img-deck-commander', className='round'),
                
                html.H3('', id='header-deck-commander'),
                
                html.Span([
                    html.Img(src="assets/w.png", width=15),
                    html.Img(src="assets/b.png", width=15),
                    html.Img(src="assets/r.png", width=15),
                ], id='span-deck-colors'),
                
                html.P('TODO: add description'),
                
                html.Div([
                    html.Button('Get Deck', id='btn-get-deck', n_clicks=0, className='primary ghost'),
                    html.Button('Deck of the Day', id='btn-get-dotd', className='primary ghost'),
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
                        dbc.Col(daq.ToggleSwitch(id='toggle-is-combo', value=True), width=8)
                    ]),


                    dbc.Row([
                        dbc.Col(html.Label('Colors'), width=4),
                        dbc.Col(dcc.RangeSlider(1, 5, 1, value=[1, 5], id='range-slider-colors'), width=8)
                    ]),

                    dbc.Row([
                        dbc.Col(html.Label('Budget'), width=4),
                        dbc.Col(daq.ToggleSwitch(id='toggle-is-budget', value=False), width=8)
                    ]),

                    dbc.Row([
                        dbc.Col(html.Label('Colors'), width=4),
                        dbc.Col(
                            html.Span([
                                html.Img(src="assets/w_.png", width=25, id='img-color-w'),
                                html.Img(src="assets/u_.png", width=25, id='img-color-u'),
                                html.Img(src="assets/b_.png", width=25, id='img-color-b'),
                                html.Img(src="assets/r_.png", width=25, id='img-color-r'),
                                html.Img(src="assets/g_.png", width=25, id='img-color-g'),
                            ]),
                        )
                    ]),

                ], id='collapse-deck-filters', is_open=False),

                html.Div([
                    html.H6('TODO: Add tags'),
                    html.Ul([
                        html.Li('Tag 1'),
                        html.Li('Tag 2'),
                        html.Li('Tag 3'),
                        html.Li('Tag 4'),
                        html.Li('Tag 5'),
                        html.Li('Tag 6')
                    ])
                ], className='skills'),

            ], className='card-container')
        ])
    ),
])



def get_dotd_idx():
    d = datetime.date.today()
    d0 = datetime.date(1970, 1, 1)
    delta = (d - d0).days
    idx = delta%GLOBAL_DECKS_DF.shape[0]
    return idx



@app.callback(
    [Output("img-deck-commander", "src"),
     Output('header-deck-commander', 'children'),
     Output('span-deck-colors', 'children'),
     Output('span-deck-budget', 'hidden')],
    [State('toggle-is-combo', 'value'),
     State('range-slider-colors', 'value'),
     State('toggle-is-budget', 'value'),
     State('img-color-w', 'src'),
     State('img-color-u', 'src'),
     State('img-color-b', 'src'),
     State('img-color-r', 'src'),
     State('img-color-g', 'src')],
    [Input("btn-get-deck", "n_clicks"),
     Input('btn-get-dotd', 'n_clicks')]
)
def get_deck(is_combo, n_colors, is_budget, w, u, b, r, g, _, __):

    # on intial load and per default get deck of the day
    idx = get_dotd_idx()

    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if input_id=='btn-get-deck':
        # print('has combo: {}'.format(is_combo))
        # print('n colors: {}'.format(n_colors))
        # print('is budget: {}'.format(is_budget))
        # print('colors: {}'.format())

        colors = [x[7] for x in [w, u, b, r, g] if not '_' in x]

        l1 = lambda x: x['is_budget']>=int(is_budget)
        l2 = lambda x: x['has_combos']<=int(is_combo)
        l3 = lambda x: n_colors[0] <= len(x['colors']) <= n_colors[1]
        l4 = lambda x: set(colors).issubset(set(x['colors']))
        
        filter = GLOBAL_DECKS_DF.apply(l1, axis=1) & GLOBAL_DECKS_DF.apply(l2, axis=1) & GLOBAL_DECKS_DF.apply(l3, axis=1) & GLOBAL_DECKS_DF.apply(l4, axis=1)

        decks_df_filtered = GLOBAL_DECKS_DF[filter]
        global GLOBAL_LAST_IDX
        
        if GLOBAL_LAST_IDX:
            decks_df_filtered = decks_df_filtered[decks_df_filtered.index != GLOBAL_LAST_IDX]
        print(decks_df_filtered.shape[0])

        if not decks_df_filtered.empty: idx = decks_df_filtered.sample(1).index.item()
        GLOBAL_LAST_IDX = idx

    name, commander_name, colors, archidekt_link, power_level, interactivity, has_combos, is_budget = GLOBAL_DECKS_DF.iloc[idx]
    commander_names = commander_name.split('/') if '/' in commander_name else ''
    if commander_names:
        commander_name = commander_names[0]

    uri = 'https://api.scryfall.com/cards/search?q={}'.format(commander_name)
    card = loads(get(uri).text)

    # handle two faced cards
    card_data = card['data'][0]
    if 'card_faces' in card_data:
        img_url = card_data['card_faces'][0]['image_uris']['art_crop']
    else:
        img_url = card_data['image_uris']['art_crop']

    # set mana symbols according to color identity
    span_deck_colors_children = [html.Img(src="assets/{}.png".format(c), width=15) for c in colors]

    return img_url, commander_name, span_deck_colors_children, not is_budget
    



# -------------------------------------------------------------------------------------------------------- #

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

# -------------------------------------------------------------------------------------------------------- #

@app.callback(Output("img-color-w", 'src'), Input("img-color-w", "n_clicks"), prevent_initial_call=True)
def toggle_img_color_w(n_clicks):
    return 'assets/w_.png' if n_clicks%2==0 else 'assets/w.png'

@app.callback(Output("img-color-u", 'src'), Input("img-color-u", "n_clicks"), prevent_initial_call=True)
def toggle_img_color_u(n_clicks):
    return 'assets/u_.png' if n_clicks%2==0 else 'assets/u.png'

@app.callback(Output("img-color-b", 'src'), Input("img-color-b", "n_clicks"), prevent_initial_call=True)
def toggle_img_color_b(n_clicks):
    return 'assets/b_.png' if n_clicks%2==0 else 'assets/b.png'

@app.callback(Output("img-color-r", 'src'), Input("img-color-r", "n_clicks"), prevent_initial_call=True)
def toggle_img_color_r(n_clicks):
    return 'assets/r_.png' if n_clicks%2==0 else 'assets/r.png'

@app.callback(Output("img-color-g", 'src'), Input("img-color-g", "n_clicks"), prevent_initial_call=True)
def toggle_img_color_g(n_clicks):
    return 'assets/g_.png' if n_clicks%2==0 else 'assets/g.png'

# -------------------------------------------------------------------------------------------------------- #


if __name__=='__main__':
    app.run_server(debug=True)
