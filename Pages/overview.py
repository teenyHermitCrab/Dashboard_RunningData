from datetime import datetime
import dash
from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import json
import pandas as pd
import plotly.express as px
from pprint import pprint as pp
import Assets.file_paths as fps
from Pages.data import df_all_runs, json_counties, fips_to_name
from Pages.sidebar import sidebar


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



def layout():
    layout_components_scatter = dbc.Row([
            dbc.Col([
                draw_scatter_all_runs()
            ], ),   #xs=12, sm=12, md=12, lg=11, xl=10, className='mt-3'
        ], className='justify-content-center')

    layout_components_maps = dbc.Row([
            dbc.Col([
                draw_total_distance()
            ],
                # adjust to screen sizes: recall there are 12 columns available.
                # for small screens (phones) use all 12 columns per element group. This forces other element group
                # to render below.  Thus for small screens, you scroll vertically instead of having to scroll in both
                # directions.
                xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3'),
            dbc.Col([
                draw_counties()
            ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3'),
        ], className='mb-4 mt-2')

    layout_about = [
        # html.Div([dash_loading_spinners.Pacman(fullscreen=True, id='loading_whole_app')], id='div_initial_loading'),
        dcc.Store(id='store_overview_page_load_trigger', data={'loaded':False}),
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
                                title='click to display plot control help',),
                              ]),
                    html.Br(),
                    html.Div([
                    dcc.Loading(dcc.Graph(id='plot_all_runs',
                                          figure = px.scatter(pd.DataFrame(), title='loading data...', template='plotly_dark'),
                                          # figure=px.scatter(df_all_runs,
                                          #                   x='start_date',
                                          #                   y='distance_miles',
                                          #                   color='total_elevation_gain_miles',
                                          #                   size='total_elevation_gain_miles',
                                          #                   hover_name='name',
                                          #                   # title='all runs',
                                          #                   color_continuous_scale=px.colors.sequential.Viridis,
                                          #                   template='plotly_dark',
                                          #                   labels={'start_date': '',
                                          #                           'distance': 'distance (meters)',
                                          #                           'distance_miles': 'distance (miles)',
                                          #                           'total_elevation_gain': 'elevation (meters)',
                                          #                           'total_elevation_gain_miles': 'elevation (miles)'},
                                          #                   hover_data={'start_date': False},
                                          #                   render_mode='auto',
                                          #                   title='all run activities'
                                          #
                                          #                   ).update_layout(title_x=0.5,
                                          #                                   autosize=True,
                                          #                                   xaxis=dict(rangeselector=dict(buttons=list([
                                          #                                       dict(count=6,
                                          #                                            label="6m",
                                          #                                            step="month",
                                          #                                            stepmode="backward"),
                                          #                                       # dict(count=1,
                                          #                                       #      label="YTD",
                                          #                                       #      step="year",
                                          #                                       #      stepmode="todate"),
                                          #                                       dict(count=1,
                                          #                                            label="1y",
                                          #                                            step="year",
                                          #                                            stepmode="backward"),
                                          #                                       dict(step="all")
                                          #                                   ]),
                                          #                                       bgcolor='#333333',
                                          #                                   ),
                                          #                                       rangeslider=dict(visible=True,
                                          #                                                        bgcolor='#444444',
                                          #                                                        ),
                                          #                                       type="date",
                                          #                                   ),
                                          #                                   ),
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
                    dcc.Markdown(id='markdown_overall_runs_plot_selected', dangerously_allow_html=False),
                    html.Br(),
                    html.Div([
                        dcc.Loading([
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
                                               # seems like I have to set this z order manually to be a low value or
                                               # else it rises all the way to top. A bug in dash leaflet?
                                               'zIndex': 1,
                                               # this is color or background on dark tile theme above
                                               # determined by color picker on screen
                                               'background':'#262626'}
                                    ),
                        ], type="cube",
                           delay_show=400,
                           overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'})
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
    fig = px.choropleth(geojson=json_counties,
                        scope="usa",
                        template='plotly_dark',
                        title='run counts per county'
                        ).update_layout(title_x=0.5,
                                        # reposition so that map fits space better - otherwise there is a lot of border
                                        margin={"r": 0,  "l": 0, 'b':15},
                                        # margin={"r": 0, "t": 0, "l": 0, "b": 0},
                                        # This made a background, but the state outlines
                                        geo=dict(landcolor='rgba(53,53,53,0.75)',)
                        ).update_coloraxes(showscale=False)

    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.Div([ ], style={'display': 'inline-block',   # style: displays element as inline-block
                                                     'vertical-align': 'top'}, ),  # style: aligns content to the top
                        html.Div([
                            dbc.Button([
                                'update county map'
                            ], id='btn_update_county_map', n_clicks=0)
                        ],
                            className='float-start',   # 'float-start' applies Bootstrap's float utility to position the element to the left
                            title='click to update county map based on current selections', ),
                    ]),
                    html.Br(),
                    dcc.Loading(dcc.Graph(id="county_count_plot",
                                          figure=fig,
                                          style={'display':'block'},  # style: forces the graph to be rendered as a block-level element

                                          config={'doubleClickDelay': 400,  # default double-click tolerance too fast for my preference, so slowing it down a bit
                                                  'displaylogo': False      #  don't show plotly logo
                                                  },
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



@callback(Output('markdown_overall_runs_plot_selected', 'children'),
          Output('distance_radius', 'radius', allow_duplicate=True),
          Output('elevation_radius', 'radius', allow_duplicate=True),
          Output('store_county_counts', 'data'),
          Input('plot_all_runs', 'relayoutData'),
          State('plot_all_runs', 'figure'),
          State('plot_all_runs', 'selectedData'),
          config_prevent_initial_callbacks=True,)
def describe_selected_runs(relay_out_data: dict, figure, selected_data):
    """
    Callback triggered when scatter plot is changed - data selection or pan/zoom

    Updates radius description, radius plots, and stores county count to dcc.Store
    (in case the update-counties-button is pressed)

    Args:
        relay_out_data (dict):
        figure (dict):
        selected_data (dict):

    Returns:
        text (str): markdown text for equivalent radius plot
        total_distance_meters (float): used for equivalent-distance circle drawn onto radius plot
        total_gain_meters (float): used for equivalent-elevation circle drawn onto radius plot
        county_counts (dict): data to be used if county plot button pressed
    """

    # TODO: check if this test necessary now that config_prevent_initial_callbacks is set
    if not relay_out_data or not figure:
        return dash.no_update

    # df_all_runs = pd.DataFrame(all_runs_data)
    # county_counts: pd.DataFrame = None

    # regardless of how plot is panned or zoomed, always display selected data if a selection is active
    if selected_data:
        points = selected_data['points']
        points_count = len(points)
        #selection = list(selected_data.keys())
        #selection.remove('points')
        #range_or_lasso = selection[0]

        point_idxs = [point['pointIndex'] for point in points]

        total_gain_meters = df_all_runs.iloc[point_idxs]['total_elevation_gain'].sum()
        total_distance_meters = df_all_runs.iloc[point_idxs]['distance'].sum()
        selection_msg = f'##### runs selected: **{points_count}**\n---\n'

        county_counts = df_all_runs.iloc[point_idxs]['county_geoid'].value_counts()
    else:
        # when no data is selected, then use the display area for choosing the points
        '''
        Yah.. this looks like a mess, but there doesn't seem to be a way to detect mouse-up events. 
        Maybe there is a javascript way to do this. or a different dash library to use...?
        But until I find that, I have to pull the displayed range off of relayoutData 
        ...or from figure? check out if there is a way to do this from figure
        
        The problem with this callback is that it updates frequently while graph is being changed, so there is alot 
        of traffic.  Need to find that mouse up event or will be stuck with having to use button to update county plot.
        '''

        # by experiment, these are the various ways the plot can be adjusted.
        initial_page_load = relay_out_data == {'autosize':True}
        range_slider_was_directly_adjusted = 'xaxis.range' in relay_out_data
        range_slider_modified_on_plot_or_zoom_buttons = 'xaxis.range[0]' in relay_out_data and 'xaxis.range[1]' in relay_out_data
        plot_buttons = 'xaxis.autorange' in relay_out_data or 'autosize' in relay_out_data

        start_date, end_date = None, None
        # print(f'{relay_out_data = }')

        if range_slider_was_directly_adjusted:    # this is where slider bars are used to adjust view
            # TODO: original DataFrame is storing dates as datetime object.  Maybe I dont need that and just keep them
            #       as strings.  Switch to strings if it seems we are not taking advantage of datetime capability.
            start_date = datetime.strptime(relay_out_data['xaxis.range'][0], '%Y-%m-%d %H:%M:%S.%f').date()
            stop_date = datetime.strptime(relay_out_data['xaxis.range'][1], '%Y-%m-%d %H:%M:%S.%f').date()
            # start_date = relay_out_data['xaxis.range'][0]
            # stop_date = relay_out_data['xaxis.range'][1]

            #msg = f'AA  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
            # print(msg, flush=True)
        elif range_slider_modified_on_plot_or_zoom_buttons:    # this is where the plot itself is dragged: pan or zoom
            start_date = datetime.strptime(relay_out_data['xaxis.range[0]'], '%Y-%m-%d %H:%M:%S.%f').date()
            stop_date = datetime.strptime(relay_out_data['xaxis.range[1]'], '%Y-%m-%d %H:%M:%S.%f').date()
            # start_date = relay_out_data['xaxis.range[0]']
            # stop_date = relay_out_data['xaxis.range[1]']
            msg = f'BB  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
            # print(msg, flush=True)
        elif initial_page_load:
            start_date = df_all_runs.iloc[0]['start_date']
            stop_date = df_all_runs.iloc[-1]['start_date']
        else: # 'xaxis.autorange' in relay_out_data or 'autosize' in relay_out_data:
            # plot control buttons pressed or axis reset
            start_date = datetime.strptime(figure['layout']['xaxis']['range'][0], '%Y-%m-%d %H:%M:%S.%f').date()
            stop_date = datetime.strptime(figure['layout']['xaxis']['range'][1], '%Y-%m-%d %H:%M:%S.%f').date()
            # start_date = figure['layout']['xaxis']['range'][0]
            # stop_date = figure['layout']['xaxis']['range'][1]
            msg = f'BB  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
            # print(msg, flush=True)

        # print(f'{start_date = } {type(start_date)}')

        mask = (df_all_runs['start_date'] >= start_date) & (df_all_runs['start_date'] <= stop_date)
        df_date_range = df_all_runs[ mask ]
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
    return  text, total_distance_meters, total_gain_meters, county_counts.to_dict('records')




@callback(Output('county_count_plot', 'figure'),
          Input('btn_update_county_map', 'n_clicks'),
          State('store_county_counts', 'data'),
          config_prevent_initial_callbacks=True
          )
def update_county_map(n_clicks: int, county_counts_data,  ):
    """
    County chloropleth map is currently updated by button click.

    Experiment with clientside callback if having this update via scatter plot relayData.  Otherwise, it is too
    slow for web server to update this.  It will likely work on a local server, but there will be unacceptable delays
    on web

    Args:
        n_clicks (int): not used in callback body, this is merely callback trigger
        county_counts_data (dict): a fairly large file with all US county data

    Returns:

        figure: (dict)  Used for county chloropleth plot.
    """
    county_counts = pd.DataFrame(county_counts_data)
    # print(f'inside button callback {type(counts) = }')

    # print(county_counts.head())
    # match up FIPS# to county name so that we can later show this name in hovertext
    # TODO: there might be a faster pandas way to combine this data.
    county_names = [fips_to_name[x] for x in county_counts['county_geoid']]
    county_counts.insert(0, 'county_name', pd.Series(county_names))
    fig = px.choropleth(county_counts,
                        geojson=json_counties,
                        locations='county_geoid',
                        color='count',
                        color_continuous_scale="Plasma",
                        # Since most of my activities are concentrated in one county, the default range
                        # would be way too wide to auto-scale colors,
                        # this low max range allows us to interpret the low-count counties
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


# NOTE: If moving these to clientside callbacks, might be able to update county plot on scatter plot move, selection.
#       But it is too slow for web server side callbacks

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



# Callback to open the modal when the page is loaded and handle checkbox state


@callback(
    Output('welcome-modal', 'is_open'),
    Output('store_quick_start', 'data'),
    Input('dont-show-checkbox', 'value'),
    State('store_quick_start', 'data'),
    # dont set config_prevent_initial_callbacks to True.  We want to take advantage of the initial callback here
)
def show_modal_on_load(dont_show, store_data):
    """
    Callback triggered on page load.

    Actually triggered by the checkbox element, because we are using

    User 'dont_show' is True, modal is not displayed.

    Args:
        dont_show (bool): checkbox value
        store_data (dcc.Store 'data' property):

    Returns:
        boolean: Sets is_open property of modal
        dict: updates dcc.Store 'data' property so that mod

    """
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



# Callback to trigger once when the page loads
@callback(
    Output('plot_all_runs', 'figure'),
    Output('distance_radius', 'radius', allow_duplicate=True),
    Output('elevation_radius', 'radius', allow_duplicate=True),
    Output("store_overview_page_load_trigger", "data"),
    Input("store_overview_page_load_trigger", "data"),
    # State('storage_df_all_runs', 'data'),
    prevent_initial_call='initial_duplicate'
    # prevent_initial_call=True  # Ensures it only runs once after initial render
)
def on_page_load(page_load_trigger_data):
    """
       Callback triggered on page load.

       Used to load the scatter plot, and radius circles on left summary map.  Will also set data for load trigger so
       this callback body won't run again.

       Currently, this runs on every page load, refresh.

       Args:
           page_load_trigger_data (dict):

       Returns:
           figure (dict) for scatter plot.
           distance_radius (float)
           elevation_radius (float)
           store_overview_page_load_trigger (dict)

       """
    if not page_load_trigger_data.get("loaded"):  # Check if page has already loaded
        # df_all_runs = pd.DataFrame(all_run_data)

        total_gain_meters = df_all_runs['total_elevation_gain'].sum()
        total_distance_meters = df_all_runs['distance'].sum()

        figure = px.scatter(df_all_runs,
                            x='start_date',
                            y='distance_miles',
                            color='total_elevation_gain_miles',
                            size='total_elevation_gain_miles',
                            hover_name='name',
                            # title='all runs',
                            color_continuous_scale=px.colors.sequential.Viridis,
                            template='plotly_dark',
                            labels={'start_date': '',
                                    'distance': 'distance (meters)',
                                    'distance_miles': 'distance (miles)',
                                    'total_elevation_gain': 'elevation (meters)',
                                    'total_elevation_gain_miles': 'elevation (miles)'},
                            hover_data={'start_date': False},
                            render_mode='auto',
                            title='all run activities'

                            ).update_layout(title_x=0.5,
                                            autosize=True,
                                            xaxis=dict(rangeselector=dict(buttons=list([
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
                                                                          bgcolor='#333333',
                                                                          ),
                                                       rangeslider=dict(visible=True,
                                                                        bgcolor='#444444',
                                                                        ),
                                                       type="date",
                                                       )
                                            )
        return figure, total_distance_meters, total_gain_meters, {'loaded':True}
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update  # Prevent unnecessary updates

