import dash
from dash import callback, dcc, html, Input, Output, Patch, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polyline

import Assets.file_paths as fps
from Pages.data import df_all_LS_runs, df_topo, Z, Z_water
from Pages.sidebar import sidebar
from pprint import pp as pp




def layout():
    """
    dash layout for Lake Sonoma page.

    Returns:

    """
    layout_components_photos = dbc.Row([
        dbc.Col([
            draw_photos()
        ], className='mt-3'),  # xs=12, sm=12, md=12, lg=11, xl=10, className='mt-3'
    ], )   # className='justify-content-center'

    layout_components_run_selector = dbc.Row([
        dbc.Col([
            draw_run_selector()
        ], className='mt-3')
    ])

    layout_components_topo = dbc.Row([
        dbc.Col([
            draw_topo_lake_sonoma()
        ],  className='mt-3'),  # xs=12, sm=12, md=6, lg=6, xl=6,
    ], )   # className='mb-4 mt-2 align-items-end'

    markdown_text = ''''''
    layout_notes = dbc.Row([
        dbc.Col([
            dcc.Markdown([markdown_text]),
        ],  className='mt-3'),  # xs=12, sm=12, md=6, lg=6, xl=6,
    ], )   #

    layout_lake_sonoma = [
        dcc.Store(id='store_lake_sonoma_page_load_trigger', data={'loaded': False}),
        sidebar(__name__),
        html.Div([
            # layout_components_scatter
            dbc.Container(layout_components_photos, fluid=True, ),
            dbc.Container(layout_components_run_selector, fluid=True),
            dbc.Container(layout_components_topo, fluid=True),
            dbc.Container(layout_notes, fluid=True),
        ], className='content')
    ]

    return layout_lake_sonoma





@callback(
    Output('plot_scatter_all_lake_sonoma_runs', 'figure'),
    Output('topo_plot_lake_sonoma', 'figure', allow_duplicate=True),
    Output("store_lake_sonoma_page_load_trigger", "data"),
    Input("store_lake_sonoma_page_load_trigger", "data"),
    # State('storage_df_lake_sonoma_all_runs', 'data',),
    # State('storage_df_topo_lake_sonoma', 'data'),
    # State('storage_nparray_lake_sonoma_Z', 'data'),
    # State('storage_nparray_lake_sonoma_Z_water', 'data'),
    prevent_initial_call='initial_duplicate'
    # prevent_initial_call=True  # Ensures it only runs once after initial render
)
def on_page_load(store_data):
    """
    Callback triggered on page load.

    Used to load the scatter and topo plots.

    Args:
        store_data (dict):

    Returns:
        figures for scatter and topo plots.  Also returns data field for load trigger, to prevent additional triggering

    """
    if not store_data.get("loaded"):  # Check if page has already loaded
        # df_all_lake_sonoma_runs = pd.DataFrame(all_lake_sonoma_run_data)

        figure = px.scatter(
            df_all_LS_runs,
            x='start_date',
            # y='distance_miles',
            y='distance',
            # color='total_elevation_gain_miles',
            # size='total_elevation_gain_miles',
            color='total_elevation_gain',
            size='total_elevation_gain',
            hover_name='name',
            # title='all runs',
            color_continuous_scale=px.colors.sequential.Viridis,
            template='plotly_dark',
            # modify displayed labels
            labels={
                'start_date': '',
                'distance': 'distance (meters)',
                'distance_miles': 'distance (miles)',
                'total_elevation_gain': 'elevation (meters)',
                'total_elevation_gain_miles': 'elevation (miles)'
            },
            hover_data={'start_date': False},
            render_mode='auto',
            title='all Lake Sonoma runs'
        )

        figure.update_layout(
            title_x=0.5,
            autosize=True,
            dragmode=None,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(
                            count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"
                        ),
                        # dict(count=1,
                        #      label="YTD",
                        #      step="year",
                        #      stepmode="todate"),
                        dict(
                            count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"
                        ),
                        dict(step="all")
                    ]),
                    bgcolor='#333333'  #  dark dark grey
                ),
                rangeslider=dict(
                    visible=True,
                    bgcolor='#444444'  # dark grey
                ),
                type="date"
            )
        )

        # hide color axis - it takes up too much space
        figure.update_layout(coloraxis_showscale=False)

        # df_topo = pd.DataFrame(topo_data)
        x = np.array(df_topo.longitude)
        y = np.array(df_topo.latitude)
        z = np.array(df_topo.elevation)
        xi = np.linspace(x.min(), x.max(), 200)  # longitude
        yi = np.linspace(y.min(), y.max(), 200)  # latitude
        # Z = np.array(z_data)
        # Z_water = np.array(z_water_data)

        fig_topo_surface = go.Figure(
            go.Surface(
                x=xi,
                y=yi,
                z=Z,
                surfacecolor=Z_water,
                opacity=0.7
            )
        )

        fig_topo_surface.update_traces(
            contours_z=dict(
                show=False,  # it gets a bit busy with this activated
                usecolormap=False,
                # highlightcolor="limegreen",
                project_z=False
            )
        )

        fig_topo_surface.update_layout(
            title=dict(text='Lake Sonoma topo test'),
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title='Elevation (m)',
                aspectmode='manual',
                # NOTE: this aspect is used to bring map close to actual lat/lon aspect ratio
                # may not have to do this once we retool the lat/lon elevation mapping
                aspectratio=dict(x=1.5, y=1.2, z=0.5)
            ),
            autosize=True,
            # scene_camera_eye=dict(x=1.87, y=0.88, z=-0.4),
            # width=1200,
            height=900,
            # margin=dict(l=65, r=50, b=65, t=90)
            template='plotly_dark',
            hovermode=False
        )

        # NOTE: no longer adding the demonstration high resolution trace
        # fig_topo_surface.add_trace(go.Scatter3d(x=df_run['longitude'],
        #                                         y=df_run['latitude'],
        #                                         z=df_run['elevation'],
        #                                         mode='lines+markers',
        #                                         name='2024 LS100K',
        #                                         marker=dict(size=3, color='red')))

        return figure, fig_topo_surface, {'loaded': True}

    return dash.no_update, dash.no_update  # Prevent unnecessary updates



def draw_photos():
    """
        Provide layout for photo carousel and map button.

    Returns:
        html.Div containing layout
    """

    # TODO: move this to markdown file.  Could store in pages folder and access by dictionary?
    markdown_text = '''
    If you are not familiar with this area: 
    '''

    # open map centered on Lake Sonoma
    map_link = r'https://www.openstreetmap.org/#map=13/38.72917/-123.06061&layers=C'

    return html.Div([
        dbc.Card(
            dbc.CardBody([
                # TODO: could make this list dynamic, based on which files match regex pattern
                dcc.Loading(
                    dbc.Carousel(items=[
                        {'key': '1', 'src': fps.page_lake_sonoma_photo_1_path},
                        {'key': '2', 'src': fps.page_lake_sonoma_photo_2_path},
                        {'key': '3', 'src': fps.page_lake_sonoma_photo_3_path},
                        {'key': '4', 'src': fps.page_lake_sonoma_photo_4_path},
                        {'key': '5', 'src': fps.page_lake_sonoma_photo_5_path},
                        {'key': '6', 'src': fps.page_lake_sonoma_photo_6_path},

                    ], controls=True,
                       indicators=True,
                       ride='carousel',
                       className='carousel-fade'),
                type='cube',
                # delay_show=500,
                delay_hide=1000,
                fullscreen=False,
                overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'}),
                html.Br(),
                # dcc.Markdown([markdown_text]),
                html.A([dbc.Button('open OpenStreetMap\nLake Sonoma', )], href=map_link, target='_blank',
                       # Bootstrap classes: left and right margins (spacing 10)
                       className='ml-10 mr-10'),
            ])
        )
    ])


def draw_scatter_all_LS_runs():
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Markdown(
                                            '* Hover over a run to show on map.\n* Click on a run to show on 3D topographic plot.'
                                        ),
                                    ],
                                    style={'display': 'inline-block', 'vertical-align': 'top'},
                                ),
                            ]
                        ),
                        html.Br(),
                        html.Div(
                            [
                                dcc.Loading(
                                    dcc.Graph(
                                        id='plot_scatter_all_lake_sonoma_runs',
                                        # a placeholder plot so we dont get a default white plot
                                        figure=px.scatter(
                                            pd.DataFrame(
                                                {'x': np.sin(np.linspace(0, 2 * np.pi, 100)) + 2}
                                            ),
                                            template='plotly_dark',
                                            title='loading data...'
                                        ),
                                        config={
                                            'doubleClickDelay': 750,
                                            'displaylogo': False,
                                            'scrollZoom': False,
                                            'displayModeBar': False,
                                            'editable': False
                                        },
                                    ),
                                    type="cube",
                                    delay_show=500,
                                    overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'}
                                ),
                            ]
                        ),
                        # dbc.Modal([
                        #     dbc.ModalHeader(dbc.ModalTitle("plot controls")),
                        #     dbc.ModalBody([modal_help_run_selection]),
                        #     # dbc.ModalFooter(dbc.Button('close',
                        #     #                            id='btn_close_plot_help',
                        #     #                            className='ms-auto',
                        #     #                            n_clicks=0))
                        # ], id='modal_plot_help', is_open=False, ),
                    ]
                )
            )
        ]
    )


def draw_lake_sonoma_map():
    # center_lat, center_lon = 38.713958, -123.031266
    center_lat, center_lon = 38.707277, -123.048768
    lake_sonoma = [center_lat, center_lon]

    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Markdown(['This is a summary polyline, not a complete set of coordinate points.'], dangerously_allow_html=False),
                    html.Br(),
                    html.Div([
                            dl.Map([
                                dl.TileLayer(
                                    url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                                    # url=
                                    # "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                    # 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                                    opacity=1.0,
                                ),
                                dl.TileLayer(
                                    url='https://a.tile.opentopomap.org/{z}/{x}/{y}.png',
                                    opacity=0.7,  # Adjust transparency to blend with the dark base map
                                    # attribution="© Wikimedia"
                                ),
                                dl.Polyline(id='selected_run_lake_sonoma',
                                            positions= [],
                                            weight=4,
                                            color='#8b0000',

                                            )
                            ],  center=lake_sonoma,
                                zoom=13,
                                attributionControl=False,
                                style={'width':'100%',
                                       'height':'27rem',
                                       'zIndex': 1,  # seems like I have to set this z order manually to be a low value
                                       # or else it rises all the way to top.  I think this is a bug/feature of dash leaflet

                                       'background':'#262626',  #this is color or background on dark tile theme above
                                       }
                            ),
                    ]),
                    # html.Div([
                    #     dcc.Markdown(['polyline: '], id='polyline_selected_run'),
                    #     dcc.Markdown(['hover data:'], id='hover_selected_run'),
                    #     ]
                    # ),
                ],
                ),
            )
        ],
    )


def draw_run_selector():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([draw_scatter_all_LS_runs()]),
                    dbc.Col([draw_lake_sonoma_map()]),
                ])
            ])
        ),
    ])


def draw_topo_lake_sonoma():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dcc.Loading([
                        dcc.Graph(id='topo_plot_lake_sonoma',
                                  figure = px.scatter(pd.DataFrame(), template='plotly_dark', title='loading data...'),
                                  config={'displaylogo': False})
                    ], type='cube',
                        delay_hide=1000,
                        fullscreen=False,
                        overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'}
                    ),
                ]),
            ])
        )
    ])




def polyline_to_dash_leaflet(encoded_polyline: str) -> list[list[float]]:
    # Decode polyline to a list of (lat, lon) tuples
    coordinates = polyline.decode(encoded_polyline)

    # Convert to Dash Leaflet format (list of [lat, lon] lists)
    dash_leaflet_polyline = [[lat, lon] for lat, lon in coordinates]

    return dash_leaflet_polyline

def polyline_to_lats_lons(encoded_polyline: str) -> (list[float], list[float]):
    # Decode polyline to a list of (lat, lon) tuples
    coordinates = polyline.decode(encoded_polyline)
    latitudes, longitudes = [coord[0] for coord in coordinates], [coord[1] for coord in coordinates]
    return latitudes, longitudes


def binary_search_find_closest_idx(nums: list[float], target: float) -> int:
    """ Binary Search - find closest index

        Find index of nums array closest to target value.

    Args:
        nums (list[float]): this array is expected to be already sorted
        target (float):

    Returns:
        integer representing index of closest value to target.
    """
    l, r = 0, len(nums) - 1
    # we don't have to use this check, but I find it to be easier to understand the algorithm
    l_prev, r_prev = -99, -99

    # <= comparison allows values outside the array (edge case is smaller values) to be tested
    # if you only use <   then you'd have to have a return statement outside while-loop
    while l <= r:
        # base case: we are now at closest point, and now need to find whether left or right is closest
        if l_prev == l and r_prev == r:
            # find whether closer to l or r ptr
            # print('now test which endpoint is closer')
            l_diff = abs(target - nums[l])
            r_diff = abs(target - nums[r])
            if l_diff <= r_diff:
                return l
            else:
                return r

        mid = (l + r) // 2
        candidate = nums[mid]
        l_prev, r_prev = l, r
        # print(f'{l=} {mid=} {r=} {candidate=}   difference: {abs(target - candidate)}')
        if target == candidate:
            return mid
        elif target < candidate:
            # don't mid + 1 here or on the left ptr.  we want to find closest but cant tell here if
            # we are closer to edges or mid.  so keep mid in both cases
            r = mid
        else:
            l = mid
    # no return here since this will exit inside while looo


@callback(Output('selected_run_lake_sonoma','positions'),
          Input('plot_scatter_all_lake_sonoma_runs', 'hoverData'),
          # State('storage_df_lake_sonoma_all_runs', 'data'),
          config_prevent_initial_callbacks=True)
def display_hover_data(hover_data):
    """
    Show a summary of run on map when hovering over scatter plot data points.

    Args:
        hover_data (dict):

    Returns:

    """
    # df_all_ls_runs = pd.DataFrame(all_ls_runs_data)
    start_date = hover_data['points'][0]['x']
    distance = hover_data['points'][0]['y']
    run_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    mask = (df_all_LS_runs['start_date'] == run_date) & (df_all_LS_runs['distance']==distance)
    summary_points = df_all_LS_runs[mask]['map.summary_polyline'].values[0]

    leaflet_format = polyline_to_dash_leaflet(summary_points)

    return leaflet_format



@callback(Output('topo_plot_lake_sonoma', 'figure', allow_duplicate=True),
          Input('plot_scatter_all_lake_sonoma_runs', 'clickData'),
          State('topo_plot_lake_sonoma', 'figure'),
          # State('storage_df_lake_sonoma_all_runs', 'data'),
          # State('storage_df_topo_lake_sonoma', 'data'),
          # State('storage_nparray_lake_sonoma_Z', 'data'),
          config_prevent_initial_callbacks=True,)
def display_click_data(click_data: dict, topo_figure: dict):
    """
    Draw run to topo map

    When user clicks on a scatter plot data point, that run is drawn onto topo map.  If a run already present on topo map
    that run will first be cleared.

    Args:
        click_data (dict):
        topo_figure (dict):

    Returns:
        Surface figure. Actually returns a Patch object to minimize data transfer
    """

    if click_data:
        print(type(click_data))
        print(type(topo_figure))
        # return f"You clicked on: {click_data['points'][0]['x']}, {click_data['points'][0]['y']}"
        # df_all_ls_runs = pd.DataFrame(all_ls_runs_data)
        # df_topo = pd.DataFrame(topo_data)
        # Z = np.array(Z_data)
        x = np.array(df_topo.longitude)
        y = np.array(df_topo.latitude)
        z = np.array(df_topo.elevation)
        xi = np.linspace(x.min(), x.max(), 200)  # longitude
        yi = np.linspace(y.min(), y.max(), 200)  # latitude
        # Z = np.array(z_data)
        # Z_water = np.array(z_water_data)

        start_date = click_data['points'][0]['x']
        distance = click_data['points'][0]['y']
        run_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        # We are masking on both start data and distance because there can be multiple runs on one day.
        mask = (df_all_LS_runs['start_date'] == run_date) & (df_all_LS_runs['distance'] == distance)
        summary_points = df_all_LS_runs[mask]['map.summary_polyline'].values[0]

        # get latitude, longitude arrays from summary points.  But summary data does not have elevation data, so we are
        # matching to closest lat/lon in the topo x-axis, y-axis.
        # NOTE: this will have to be adjusted when we refine the topo surface to not use meshgrid
        lats, lons, = polyline_to_lats_lons(summary_points)
        # now find the index where that element's value is closest
        lons_idx = [binary_search_find_closest_idx(xi, x) for x in lons]
        lats_idx = [binary_search_find_closest_idx(yi, y) for y in lats]

        # use that closest index to get lat/lons from xi, yi (because this is what the Surface topo is using)
        lons_adjusted = [xi[x] for x in lons_idx]
        lats_adjusted = [yi[y] for y in lats_idx]

        # since we are now using the closest lat/lons on the Surface topo (closest to our run summary), our elevations
        # that we use from Z will land directly on the surface plot. they will not float above or below.
        elevations = [float(Z[z[0]][z[1]]) for z in zip(lats_idx, lons_idx)]
        df_specific_run = pd.DataFrame({'latitude': lats_adjusted, 'longitude': lons_adjusted, 'elevation': elevations})

        new_scatter = go.Scatter3d(x=df_specific_run['longitude'],
                                   y=df_specific_run['latitude'],
                                   z=df_specific_run['elevation'],
                                   mode='lines+markers',
                                   # name='2024 LS100K',
                                   marker=dict(size=3, color='red'))

        patch = Patch()
        data = topo_figure.get("data", [])

        # We only want to show this one summary on the Surface topo, so need to get rid of previous.
        for i, trace in enumerate(data):
            if trace.get("type") == "scatter3d":
                # Replace the Scatter3d trace with the new one using the patch syntax
                # Note: I think there was old patch syntax where the assignment was a string.
                # e.g., patch[f'['data']{i}']  or similar
                patch['data'][i] = new_scatter
                break  # Exit after the first match, but could make this general and delete all current Scatter3d traces
        else:
            # if for-loop didn't encounter a break, then where was no Scatter3d already present
            # Note: this code would leave other non-Scatter3d traces.
            patch['data'] = data + [new_scatter]



        return patch
    else:
        raise PreventUpdate

