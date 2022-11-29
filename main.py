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
                html.Span('Deck of the Day', className='pro-2', id='span-deck-of-the-day'),
                
                html.Img(src='', width=200, id='img-deck-commander', className='round'),
                
                html.H3('', id='header-deck-commander'),
                
                html.Span([
                    html.Img(src="assets/w.png", width=15),
                    html.Img(src="assets/b.png", width=15),
                    html.Img(src="assets/r.png", width=15),
                ], id='span-deck-colors'),
                
                html.P(id='p-deck-description'),
                
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

                    dbc.Row([
                        dbc.Col(html.Label('Powerlevel'), width=4),
                        dbc.Col(dcc.RangeSlider(1, 10, 1, value=[1, 10], id='range-slider-power-level'), width=8)
                    ], className='filter'),

                    dbc.Row([
                        dbc.Col(html.Label('Interactivity'), width=4),
                        dbc.Col(dcc.RangeSlider(1, 10, 1, value=[1, 10], id='range-slider-interactivity'), width=8)
                    ]),

                ], id='collapse-deck-filters', is_open=False),

                html.Div([
                    html.H6('Tags'),
                    html.Ul(id='ul-tags')
                ], className='skills'),

            ], className='card-container')
        ])
    ),
])



# get random deck from todays date
def get_dotd_idx():
    d = datetime.date.today()
    d0 = datetime.date(1970, 1, 1)
    delta = (d - d0).days
    idx = delta%GLOBAL_DECKS_DF.shape[0]
    return idx



# handle deck selection callback
@app.callback(
    [Output("img-deck-commander", "src"),
     Output('header-deck-commander', 'children'),
     Output('span-deck-colors', 'children'),
     Output('span-deck-budget', 'hidden'),
     Output('p-deck-description', 'children'),
     Output('ul-tags', 'children'),
     Output('span-deck-of-the-day', 'hidden')],
    [State('toggle-is-combo', 'value'),
     State('range-slider-colors', 'value'),
     State('toggle-is-budget', 'value'),
     State('img-color-w', 'src'),
     State('img-color-u', 'src'),
     State('img-color-b', 'src'),
     State('img-color-r', 'src'),
     State('img-color-g', 'src'),
     State('range-slider-power-level', 'value'),
     State('range-slider-interactivity', 'value')],
    [Input("btn-get-deck", "n_clicks"),
     Input('btn-get-dotd', 'n_clicks')]
)
def get_deck(is_combo, n_colors, is_budget, w, u, b, r, g, power_level, interactivity, _, __):

    # on intial load and per default get deck of the day
    idx = get_dotd_idx()

    # if get-deck was clicked, select a random deck according to filters
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if input_id=='btn-get-deck':

        # filter colors from the image sources
        colors = [x[7] for x in [w, u, b, r, g] if not '_' in x]

        # initialize lambda filter functions
        l1 = lambda x: x['is_budget']>=int(is_budget)
        l2 = lambda x: x['has_combos']<=int(is_combo)
        l3 = lambda x: n_colors[0] <= len(x['colors']) <= n_colors[1]
        l4 = lambda x: set(colors).issubset(set(x['colors']))
        l5 = lambda x: power_level[0] <= x['power_level'] <= power_level[1]
        l6 = lambda x: interactivity[0] <= x['interactivity'] <= interactivity[1]
        
        # filter the subset of decks that fulfill the filter criteria
        filter = GLOBAL_DECKS_DF.apply(l1, axis=1) & GLOBAL_DECKS_DF.apply(l2, axis=1) &\
            GLOBAL_DECKS_DF.apply(l3, axis=1) & GLOBAL_DECKS_DF.apply(l4, axis=1) &\
            GLOBAL_DECKS_DF.apply(l5, axis=1) & GLOBAL_DECKS_DF.apply(l6, axis=1)

        # filter the dataframe
        decks_df_filtered = GLOBAL_DECKS_DF[filter]
        global GLOBAL_LAST_IDX

        # pick an different 'random' deck each time
        if GLOBAL_LAST_IDX:
            decks_df_filtered = decks_df_filtered[decks_df_filtered.index != GLOBAL_LAST_IDX]

        # select deck of the day if selection is empty
        if not decks_df_filtered.empty: idx = decks_df_filtered.sample(1).index.item()
        GLOBAL_LAST_IDX = idx

    dotd = True if idx==get_dotd_idx() else False

    # get the deck information
    name, commander_name, colors, archidekt_link, power_level, interactivity, has_combos, is_budget = GLOBAL_DECKS_DF.iloc[idx]
    
    # TODO: add tags
    ul_tags_children=[
        html.Li('Spicy Brew'),
        html.Li('Budget'),
        html.Li('Full Old Border'),
        html.Li('Only German Cards'),
        html.Li('Free Spells'),
        html.Li('Battlecruiser')
    ]

    p_deck_description_children = 'Some description about the deck, its unique features, maybe highlight some special cards. Talk about the win-con or some history on the deck.'

    # handle multiple commanders
    # TODO: create split image
    commander_names = commander_name.split('/') if '/' in commander_name else ''
    if commander_names:
        commander_name = commander_names[0]

    # get card info from scryfall
    uri = 'https://api.scryfall.com/cards/search?q={}'.format(commander_name)
    card = loads(get(uri).text)

    # handle two faced cards - pick front by default
    card_data = card['data'][0]
    if 'card_faces' in card_data:
        img_url = card_data['card_faces'][0]['image_uris']['art_crop']
    else:
        img_url = card_data['image_uris']['art_crop']

    # set mana symbols according to color identity
    span_deck_colors_children = [html.Img(src="assets/{}.png".format(c), width=15) for c in colors]

    return img_url, commander_name, span_deck_colors_children, not is_budget, p_deck_description_children, ul_tags_children, not dotd
    


# collapse filters
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



# toggle selected mana symbol colors
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



if __name__=='__main__':
    app.run_server(debug=True)
