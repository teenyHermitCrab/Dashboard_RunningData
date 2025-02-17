from datetime import datetime
import dash
from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_loading_spinners
import json
import pandas as pd
import plotly.express as px
from pprint import pprint as pp
from Pages.sidebar import sidebar


import Assets.file_paths as fps




##### get my saved, processed data
df_all_names_scrubbed = pd.read_pickle(fps.page_overview_all_runs_df_path)

# with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
#     counties = json.load(response)

# this is used for choropleth county outlines.  Contains outline data for all counties and is needed for `geojson` parameter
with open(fps.page_overview_geojson_fips_path, 'r') as f:
    counties = json.load(f)


#########################  no need to do this all the time, just save the data.
# maybe county names can change
# df_fips = df_all_names_scrubbed.loc[:, ['county', 'county_geoid']]
# df_fips.reset_index(inplace=True)
#
# fips_to_name = {}
# for idx, row in df_fips.iterrows():
#     fips_to_name[row['county_geoid']] = row['county']
#
# pd.to_pickle(fips_to_name, r'./assets/fips_to_name.pkl')
#########################


fips_to_name =pd.read_pickle(fps.page_overview_fips_to_name_df_pickle_path)


#region modal plot help

# TODO: move this to static files or file in pages folder
text_modal_help = '''
* Pan or zoom the plot using range slider handles or plot buttons.
* Elevation and gain radius plots will automatically update.
* Click button to update county count map.
'''

modal_help_run_selection = html.Div([
        dcc.Markdown(text_modal_help),
        html.Hr(),
        dbc.Row(dbc.Col( html.Div([
                                    html.Video(src=fps.page_overview_plot_quick_start_path,
                                               controls=True,
                                               muted=True,
                                               autoPlay=True,  # start playing video automatically
                                               style={'width': '100%', 'height':'auto'}),
                                  ], style={'width': '100%'} )  # Ensure the container also stretches
                        )
        ),
    ])


@callback(Output("modal_plot_help", "is_open"),
          Input("btn_open_plot_help", "n_clicks"),
          # Input("btn_close_plot_help", "n_clicks"),
          State("modal_plot_help", "is_open"))
def toggle_modal_plot_help(n1, is_open):
    if n1:
        return not is_open
    return is_open
#endregion


#region initial modal

# TODO: move this to static files
text_modal_quick_start = '''
* Pan or zoom the plot using range slider handles or plot buttons.
* Elevation and gain radius plots will automatically update.
* Click button to update county count map.
'''


modal_quick_start_guide = html.Div([
        dcc.Markdown(text_modal_quick_start),
        html.Hr(),
        dbc.Row(dbc.Col( html.Div([
                                    html.Video(src=fps.page_overview_plot_quick_start_path,
                                               controls=True,
                                               muted=True,
                                               autoPlay=True,  # start playing video automatically
                                               style={'width': '100%', 'height':'auto'}),
                                  ], style={'width': '100%'} )  # Ensure the container also stretches
                        )
        ),
    ])

#endregion


@callback(Output('sidebar', 'className'),  #className
    Input('sidebarCollapse', 'n_clicks'),
    State('sidebar', 'className'))
def toggle_sidebar(btn_click, className):
    # print(f' toggle button: {btn_click}   {className =}')
    if className == 'active':
        return ''
    if className == '':
        return 'active'


def draw_scatter_all_runs():
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                              html.Div([
                                        #html.H5('all run activities')
                                       ],style={'display': 'inline-block', 'vertical-align': 'top'},),
                              html.Div([
                                  dbc.Button([
                                                        #html.I(className="fa-regular fa-circle-question me-3 fa-1x"),
                                                        '  help'
                                                     ],
                                                   id='btn_open_plot_help', n_clicks=0)
                              ],
                                className='float-end',
                                # style={'display': 'inline-block', 'vertical-align': 'top'},
                                title='click to display plot control help',),
                              ]),
                    html.Br(),
                    html.Div([
                    dcc.Loading(dcc.Graph(id='plot_all_runs',
                                          figure=px.scatter(df_all_names_scrubbed,
                                                            x='start_date',
                                                            y='distance_miles',
                                                            color='total_elevation_gain_miles',
                                                            size='total_elevation_gain_miles',
                                                            hover_name='name',
                                                            #title='all runs',
                                                            color_continuous_scale=px.colors.sequential.Viridis,
                                                            template='plotly_dark',
                                                            labels={'start_date':'',
                                                                    'distance':'distance (meters)',
                                                                    'distance_miles':'distance (miles)',
                                                                    'total_elevation_gain':'elevation (meters)',
                                                                    'total_elevation_gain_miles':'elevation (miles)'},
                                                            hover_data={'start_date':False},
                                                            render_mode='auto',
                                                            title='all run activities'

                                                            )#.update_layout(title_x=0.5, autosize=True),
                                                            .update_layout(
                                                                # title='all runs',
                                                                title_x=0.5,
                                                                autosize=True,
                                                                xaxis=dict(
                                                                    rangeselector=dict(
                                                                        buttons=list([
                                                                            dict(count=6,
                                                                                 label="6m",
                                                                                 step="month",
                                                                                 stepmode="backward"),
                                                                            # dict(count=1,
                                                                            #      label="YTD",
                                                                            #      step="year",
                                                                            #      stepmode="todate"),
                                                                            dict(count=1,
                                                                                 label="1y",
                                                                                 step="year",
                                                                                 stepmode="backward"),
                                                                            dict(step="all")
                                                                        ]),
                                                                        bgcolor='#333333'

                                                                    ),
                                                                    rangeslider=dict(
                                                                        visible=True,
                                                                        bgcolor='#444444'
                                                                    ),
                                                                    type="date",
                                                                )
                                                            ),
                                          # default double-click is really fast, dont show plotly logo
                                          config={'doubleClickDelay':750, 'displaylogo': False},
                                          ),
                                type="cube",
                                delay_show=500,
                                overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'}
                                ),
                    ]),
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle("plot controls")),
                        dbc.ModalBody([modal_help_run_selection]),
                        # dbc.ModalFooter(dbc.Button('close',
                        #                            id='btn_close_plot_help',
                        #                            className='ms-auto',
                        #                            n_clicks=0))
                    ], id='modal_plot_help', is_open=False, ),
                ], ),
            )
        ],
    )


def draw_total_distance():
    center_lat = 38.713958
    center_lon = -123.031266
    lake_sonoma = [center_lat, center_lon]
    #hawaii_kalalau_trail = [22.193489, -159.628206]
    pacific_ocean_near_dateline = [38.753608, -179.800167]

    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Markdown(id='txt_overall_runs_plot_selected', dangerously_allow_html=False),
                    html.Br(),
                    html.Div([
                            dl.Map([
                                dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', ),
                                dl.Marker(position=lake_sonoma,
                                          children=[dl.Popup(content='Lake Sonoma, CA')]),
                                dl.Circle(id='distance_radius', center=lake_sonoma, radius=0),
                                dl.Circle(id='elevation_radius', center=lake_sonoma, radius=0, color='#D67220'),
                            ],  center=pacific_ocean_near_dateline,
                                zoom=1,
                                attributionControl=False,
                                style={'width':'100%',
                                       'height':'20rem',
                                       'zIndex': 1,  # seems like I have to set this z order manually to be a low value or else it rises all the way to top
                                       # this is color or background on dark tile theme above
                                       # determined by color picker on screen
                                       'background':'#262626'}
                            ),
                    ]),
                    dcc.Markdown(['\n<sub>Distortions of circles result from map projection.</sub> '],
                                 style={'textAlign':'center'},
                                 dangerously_allow_html=True),
                ],
                ),
            )
        ],
    )


def draw_counties():
    fig = px.choropleth(geojson=counties,
                        scope="usa",
                        template='plotly_dark',
                        title='run counts per county'
                        ).update_layout(title_x=0.5,
                                        margin={"r": 0,  "l": 0, 'b':15},
                                        # margin={"r": 0, "t": 0, "l": 0, "b": 0},
                                        # This made a background, but the state outlines
                                        geo=dict(landcolor='rgba(53,53,53,0.75)',)
                        ).update_coloraxes(showscale=False)

    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.Div([ ], style={'display': 'inline-block', 'vertical-align': 'top'}, ),
                        html.Div([
                            dbc.Button([
                                # html.I(className="fa-regular fa-circle-question me-3 fa-1x"),
                                'update county map'
                            ],
                                id='btn_update_county_map', n_clicks=0)
                        ],
                            className='float-start',
                            # style={'display': 'inline-block', 'vertical-align': 'top'},
                            title='click to update county map based on current selections', ),
                    ]),
                    html.Br(),
                    dcc.Loading(dcc.Graph(id="county_count_plot",
                                          figure=fig,
                                          style={'display':'block'},
                                          # default double-click is really fast, don't' show plotly logo
                                          config={'doubleClickDelay': 400, 'displaylogo': False},
                                          ),
                                type="cube",
                                #delay_show=500,
                                overlay_style={'visibility':'visible',
                                               'filter':'blur(3px)'}),
                    html.Br(),
                    dcc.Store(id='store_county_counts')
                ])
            )
        ])



def meters_to_miles(meters: float) -> float:
    return meters * 0.000621371

# @callback(Output('txt_overall_runs_plot_selected', 'children'),
#               Input('plot_all_runs', 'selectedData'))
# def describe_selected_runs(selected_data: dict):
#     if selected_data:
#         points = selected_data['points']
#         points_count = len(points)
#         selection = list(selected_data.keys())
#         selection.remove('points')
#         #range_or_lasso = selection[0]
#
#         point_indicies = [point['pointIndex'] for point in points]
#
#         #elevations = df_all_names_scrubbed.iloc[point_indicies]['total_elevation_gain']
#         # max_x = max(selected_data[range_or_lasso]['x'])
#         # min_x = min(selected_data[range_or_lasso]['x'])
#         # max_y = max(selected_data[range_or_lasso]['y'])
#         # min_y = min(selected_data[range_or_lasso]['y'])
#         # area = (max_x-min_x) *  (max_y-min_y)
#         # if area == 0:
#         #     return f'area selected is zero'
#         # density = points_count/area
#
#         total_gain_meters = df_all_names_scrubbed.iloc[point_indicies]['total_elevation_gain'].sum()
#         total_distance_meters = df_all_names_scrubbed.iloc[point_indicies]['distance'].sum()
#         selection_msg = f'##### runs selected: **{points_count}**\n---\n'
#     else:
#         counts = df_all_names_scrubbed['county_geoid'].value_counts()
#
#         total_gain_meters = df_all_names_scrubbed['total_elevation_gain'].sum()
#         total_distance_meters = df_all_names_scrubbed['distance'].sum()
#         selection_msg = f'##### no runs selected  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- use entire history\n---'
#
#     miles_gain, km_gain = meters_to_miles(total_gain_meters), total_gain_meters / 1000.0
#     miles_dist, km_dist = meters_to_miles(total_distance_meters), total_distance_meters / 1000.0
#     # ({km_dist:,.1f} km)   ({km_gain:,.1f} km)
#     distance_msg = f'- distance:&nbsp;&nbsp;&nbsp;**{miles_dist:,.1f}** miles  🔵 blue circle'
#     elevation_msg = f'- elevation:&nbsp&nbsp;**{miles_gain:,.1f}** miles  🟠 orange circle'
#     text = f'{selection_msg}\n{distance_msg}\n{elevation_msg}\n'
#
#     return  text


@callback(Output('txt_overall_runs_plot_selected', 'children'),
          Output('distance_radius', 'radius'),
          Output('elevation_radius', 'radius'),
          Output('store_county_counts', 'data'),
          Input('plot_all_runs', 'relayoutData'),
          State('plot_all_runs', 'figure'),
          State('plot_all_runs', 'selectedData'))
def describe_selected_runs(relay_out_data: dict, figure, selected_data):
    if not relay_out_data:
        return dash.no_update

    #print(f'###############\n{selected_data}')
    # regardless of how plot is panned or zoomed, always display selected data if a selection is active
    if selected_data:
        points = selected_data['points']
        points_count = len(points)
        #selection = list(selected_data.keys())
        #selection.remove('points')
        #range_or_lasso = selection[0]

        point_idxs = [point['pointIndex'] for point in points]

        total_gain_meters = df_all_names_scrubbed.iloc[point_idxs]['total_elevation_gain'].sum()
        total_distance_meters = df_all_names_scrubbed.iloc[point_idxs]['distance'].sum()
        selection_msg = f'##### runs selected: **{points_count}**\n---\n'

        county_counts = df_all_names_scrubbed['county_geoid'].value_counts()

    else:
        # when no data is selected, then use the display area for choosing the points
        '''
        Yah.. this looks like a mess, but there doesn't seem to be a way to detect mouse-up events. 
        Maybe there is a javascript way to do this. or a different dash library to use.
        But until I find that, I have to pull the displayed range off of relayoutData or from figure
        Hmmm... should probably just do this from figure.
        
        The problem with this callback is that it updates frequently while graph is being changed, so there is alot 
        of traffic.  Need to find that mouse up event 
        '''

        range_slider_was_directly_adjusted = 'xaxis.range' in relay_out_data
        range_slider_modified_on_plot_or_zoom_buttons = 'xaxis.range[0]' in relay_out_data and 'xaxis.range[1]' in relay_out_data
        plot_buttons = 'xaxis.autorange' in relay_out_data or 'autosize' in relay_out_data

        start_date, end_date = None, None
        # print(f'{relay_out_data = }')

        if range_slider_was_directly_adjusted:    # this is where slider bars are used to adjust view
            start_date = datetime.strptime(relay_out_data['xaxis.range'][0], '%Y-%m-%d %H:%M:%S.%f').date()
            stop_date = datetime.strptime(relay_out_data['xaxis.range'][1], '%Y-%m-%d %H:%M:%S.%f').date()
            #msg = f'AA  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
            # print(msg, flush=True)
        elif range_slider_modified_on_plot_or_zoom_buttons:    # this is where the plot itself is dragged: pan or zoom
            start_date = datetime.strptime(relay_out_data['xaxis.range[0]'], '%Y-%m-%d %H:%M:%S.%f').date()
            stop_date = datetime.strptime(relay_out_data['xaxis.range[1]'], '%Y-%m-%d %H:%M:%S.%f').date()
            msg = f'BB  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
            # print(msg, flush=True)
        else: # 'xaxis.autorange' in relay_out_data or 'autosize' in relay_out_data:
            # plot control buttons pressed or axis reset
            start_date = datetime.strptime(figure['layout']['xaxis']['range'][0], '%Y-%m-%d %H:%M:%S.%f').date()
            stop_date = datetime.strptime(figure['layout']['xaxis']['range'][1], '%Y-%m-%d %H:%M:%S.%f').date()
            msg = f'BB  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
            # print(msg, flush=True)

        mask = (df_all_names_scrubbed['start_date'] >= start_date) & (df_all_names_scrubbed['start_date'] <= stop_date)
        df_date_range = df_all_names_scrubbed[ mask ]
        total_gain_meters = df_date_range['total_elevation_gain'].sum()
        total_distance_meters = df_date_range['distance'].sum()
        selection_msg = f'##### runs selected: **{len(df_date_range)}**\n---\n'

        county_counts = df_date_range['county_geoid'].value_counts()

    miles_gain, km_gain = meters_to_miles(total_gain_meters), total_gain_meters / 1000.0
    miles_dist, km_dist = meters_to_miles(total_distance_meters), total_distance_meters / 1000.0
    # ({km_dist:,.1f} km)   ({km_gain:,.1f} km)
    distance_msg = f'- total distance:&nbsp;&nbsp;&nbsp;**{miles_dist:,.1f}** miles  🔵 blue circle'
    elevation_msg = f'- total elevation:&nbsp&nbsp;**{miles_gain:,.1f}** miles  🟠 orange circle'
    text = f'{selection_msg}\n{distance_msg}\n{elevation_msg}\n'


    # store this dataframe of county counts so that update-county-plot button can use it
    county_counts = pd.DataFrame(county_counts)
    county_counts.reset_index(inplace=True)
    # print(f'{type(county_counts) = }')
    # print(county_counts)
    return  text, total_distance_meters, total_gain_meters, county_counts.to_dict('records')



@callback(Output('county_count_plot', 'figure'),
          Input('btn_update_county_map', 'n_clicks'),
          State('store_county_counts', 'data'),
          config_prevent_initial_callbacks=True
          )
def update_county_map(n_clicks: int, counts):
    county_counts = pd.DataFrame(counts)
    # print(f'inside button callback {type(counts) = }')

    # print(county_counts.head())
    # match up FIPS# to county name so that we can later show this name in hovertext
    # TODO: there might be a faster pandas way to combine this data.
    county_names = [fips_to_name[x] for x in county_counts['county_geoid']]
    county_counts.insert(0, 'county_name', pd.Series(county_names))
    fig = px.choropleth(county_counts,
                        geojson=counties,
                        locations='county_geoid',
                        color='count',
                        color_continuous_scale="Plasma",
                        # the range is way too wide to auto-scale colors,
                        # this low max allows us to interpret the low-count counties
                        range_color=(0, 15),
                        scope='usa',
                        hover_name='county_name',
                        # no need to show FIPS# on hover - it doesn't mean much to user
                        hover_data={'county_geoid': False},
                        template='plotly_dark',
                        title='run counts per county',

                        ).update_layout(
                                        # center title on plot
                                        title_x=0.5,
                                        # left,right borders to zero to keep map more visible
                                        margin={"r": 0,  "l": 0, 'b':15},
                                        # slight adjustment of landcolor allows dark color counts to be more visible
                                        geo=dict(landcolor='rgba(53,53,53,0.75)',
                                                 #bgcolor='rgba(50,50,50, 0.75)'
                                                 ),

                        ).update_coloraxes(showscale=False)

    return fig#, {'display':'block', }


# @callback(Output('county_count_plot', 'figure'),
#           #Output('county_count_plot', 'style'),
#           Input('plot_all_runs', 'selectedData'))
# def update_county_map(selected_data: dict):
#     if selected_data:
#         points = selected_data['points']
#         # selection = list(selected_data.keys())
#         # selection.remove('points')
#         # range_or_lasso = selection[0]
#
#         # get index of data points selected
#         point_indicies = [point['pointIndex'] for point in points]
#
#         # pandas Series: county counts of only points selected
#         counts = df_all_names_scrubbed.iloc[point_indicies]['county_geoid'].value_counts()
#
#     else:
#         # pandas Series: county counts of all data
#         counts = df_all_names_scrubbed['county_geoid'].value_counts()
#
#     # create a dataframe that has county_geoid, count, county_name.  This will be
#     # dataframe used by choropleth plot
#     county_counts = pd.DataFrame(counts)
#     county_counts.reset_index(inplace=True)
#     # match up FIPS# to county name so that we can later show this name in hovertext
#     # TODO: there might be a faster pandas way to combine this data.
#     county_names = [fips_to_name[x] for x in county_counts['county_geoid']]
#     county_counts.insert(0, 'county_name', pd.Series(county_names))
#     fig = px.choropleth(county_counts,
#                         geojson=counties,
#                         locations='county_geoid',
#                         color='count',
#                         color_continuous_scale="Plasma",
#                         # the range is way too wide to auto-scale colors,
#                         # this low max allows us to interpret the low-count counties
#                         range_color=(0, 15),
#                         scope='usa',
#                         hover_name='county_name',
#                         # no need to show FIPS# on hover - it doesn't mean much to user
#                         hover_data={'county_geoid': False},
#                         template='plotly_dark',
#                         title='run counts per county',
#
#                         ).update_layout(
#                                         # center title on plot
#                                         title_x=0.5,
#                                         # left,right borders to zero to keep map more visible
#                                         margin={"r": 0,  "l": 0, 'b':15},
#                                         # slight adjustment of landcolor allows dark color counts to be more visible
#                                         geo=dict(landcolor='rgba(53,53,53,0.75)',
#                                                  #bgcolor='rgba(50,50,50, 0.75)'
#                                                  ),
#
#                         ).update_coloraxes(showscale=False)
#
#
#     return fig#, {'display':'block', }




# @callback(Output('distance_radius', 'radius'),
#               Output('elevation_radius', 'radius'),
#               Input('plot_all_runs', 'selectedData'))
# def update_distance_circle(selected_data: dict):
#     if selected_data:
#         points = selected_data['points']
#         #points_count = len(points)
#         selection = list(selected_data.keys())
#         selection.remove('points')
#         #range_or_lasso = selection[0]
#
#         point_indicies = [point['pointIndex'] for point in points]
#
#         total_distance_meters = df_all_names_scrubbed.iloc[point_indicies]['distance'].sum()
#         total_gain_meters = df_all_names_scrubbed.iloc[point_indicies]['total_elevation_gain'].sum()
#
#         return total_distance_meters, total_gain_meters
#     else:
#         total_distance_meters = df_all_names_scrubbed['distance'].sum()
#         total_gain_meters = df_all_names_scrubbed['total_elevation_gain'].sum()
#
#         return total_distance_meters, total_gain_meters


# Callback to open the modal when the page is loaded and handle checkbox state


@callback(
    Output('welcome-modal', 'is_open'),
    Output('store_quick_start', 'data'),
    Input('dont-show-checkbox', 'value'),
    State('store_quick_start', 'data'),
    # config_prevent_initial_callbacks=True,
)
def show_modal_on_load(dont_show, store_data):
    # Parse the stored data from dcc.Store
    store_data = json.loads(store_data)

    # If 'dont_show' is checked, update the store to prevent future modals
    if dont_show:
        store_data['modal_shown'] = True
        return False, json.dumps(store_data)  # Close the modal and update store

    # If modal_shown is False, show the modal on page load
    if not store_data.get('modal_shown', False):
        return True, json.dumps(store_data)  # Open the modal

    return False, json.dumps(store_data)  # Don't show the modal if already marked


#
# @callback(Output('div_initial_loading', 'children'),
#           Input('div_overview_content', 'loading_state'),
#           State('div_initial_loading', 'children'),
# )
# def hide_initial_spinner_after_startup(loading_state, children):
#     if children:
#         return None
#     raise PreventUpdate


def layout():
    layout_components_scatter = dbc.Row([
            dbc.Col([
                draw_scatter_all_runs()
            ], ),   #xs=12, sm=12, md=12, lg=11, xl=10, className='mt-3'
        ], className='justify-content-center')

    layout_components_maps = dbc.Row([
            dbc.Col([
                draw_total_distance()
            ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3'),
            dbc.Col([
                draw_counties()
            ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3'),
        ], className='mb-4 mt-2')  # align-items-end

    layout_about = [
        # html.Div([dash_loading_spinners.Pacman(fullscreen=True, id='loading_whole_app')], id='div_initial_loading'),
        sidebar(__name__),
        html.Div([
            # layout_components_scatter
            dbc.Container(layout_components_scatter,  fluid=True,),
            dbc.Container(layout_components_maps, fluid='md')
        ], id='div_overview_content', className='content'),
        # dcc.Store to keep track of whether the quick-start modal should be shown or not
        dcc.Store(id='store_quick_start', storage_type='session', data=json.dumps({'modal_shown': False})),
        dbc.Modal(
            [
                dbc.ModalHeader(dcc.Markdown("##### How to select data", style={'textAlign':'center'})),
                dbc.ModalBody(modal_quick_start_guide),
                dbc.ModalFooter(
                    dbc.Checklist(options=[{'label': 'Do not show at page open', 'value': 'dont_show'}],
                                  id='dont-show-checkbox',
                                  inline=True,
                                  style={'margin': 'auto'}
                    )
                )
            ],
            id='welcome-modal',
            is_open=False,  # Modal is initially closed
        ),
    ]

    return layout_about