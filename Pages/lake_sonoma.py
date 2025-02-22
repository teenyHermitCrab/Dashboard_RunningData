import dash
from dash import callback, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import polyline
from dash.exceptions import PreventUpdate

import Assets.file_paths as fps
from Pages.sidebar import sidebar
from pprint import pp as pp


df_all_LS_runs = pd.read_pickle(fps.page_lake_sonoma_df_all_runs_path)

# lake_sonoma =  r'./topos/topo_lake_sonoma_35m.csv'
# df = pd.read_csv(lake_sonoma)
#
# # Lake Sonoma lake level.  Only doing this west of the dam.  The land east of dam is lower than
# df.loc[(df['elevation'] < 142) & (df['longitude'] < -123.0092), 'elevation'] = 142

# # Merlo Lake  - this bounding box should be tightened up and use less than 145 (not < 0) to get a flat surface
# df.loc[(df['elevation'] < 0) & (df['longitude'] > -123.001) & (df['latitude'] < 38.7), 'elevation'] = 145
# #df.elevation.nsmallest()
# pd.to_pickle(df, r'./topos/df_topo_lake_sonoma_35m.pkl')

topo_pickle_path = fps.page_lake_sonoma_topo_map_path
df = pd.read_pickle(topo_pickle_path)
ls_run_file = fps.page_lake_sonoma_100K_run_path

df_run = pd.read_csv(ls_run_file)
df_run['elevation'] = df_run['elevation'] + 3

x = np.array(df.longitude)
y = np.array(df.latitude)
z = np.array(df.elevation)

xi = np.linspace(x.min(), x.max(), 200)  # longitude
yi = np.linspace(y.min(), y.max(), 200)  # latitude

# print(yi)
# print(len(yi))
df_evenly_spaced = pd.DataFrame({'longitude': xi, 'latitude': yi})



# X,Y = np.meshgrid(xi,yi)
# # print('meshgrid DONE')
#
# Z = griddata((x,y),z,(X,Y), method='cubic')  #cubic, nearest
# print(type(Z))
# # print('griddata DONE')
#
# # could probably pre-process Z here to manually substitute lake values?
# Z_water = Z.copy()
# Z_water[(Z_water > 141.9) & (142.1 > Z_water)] = 300
#
# pd.to_pickle(Z, r'./topos/np_griddata_topo_lake_sonoma_35m.pkl')
# pd.to_pickle(Z_water, r'./topos/np_griddata_surfacecolor_water_topo_lake_sonoma_35m.pkl')



Z = pd.read_pickle(fps.page_lake_sonoma_topo_z_data_path)
Z_water = pd.read_pickle(fps.page_lake_sonoma_topo_z_water_data_path)

# print(Z)

fig = go.Figure(go.Surface(x=xi,y=yi,z=Z,
                           surfacecolor=Z_water,
                           opacity=0.7,
                           ),
                )


fig.update_traces(contours_z=dict(show=False,
                                  usecolormap=False,
                                  # highlightcolor="limegreen",
                                  project_z=False
                                  )
                  )
fig.update_layout(title=dict(text='Lake Sonoma - 2024 100K (full resolution)'),
                  scene = dict(xaxis_title='Longitude',
                               yaxis_title='Latitude',
                               zaxis_title='Elevation (m)',
                               aspectmode = 'manual',
                               aspectratio = dict(x=1.5, y=1.2, z=0.5),   #
                               ),
                  autosize=True,
                  #scene_camera_eye=dict(x=1.87, y=0.88, z=-0.4),
                  #width=1200,
                  height=900,
                  #margin=dict(l=65, r=50, b=65, t=90)
                  template='plotly_dark',
                  hovermode=False,
)


fig.add_trace(go.Scatter3d(x=df_run['longitude'],
                           y=df_run['latitude'],
                           z=df_run['elevation'],
                           mode='lines+markers',
                           name='2024 LS100K',
                           marker=dict(size=3, color='red')))



def draw_photos():
    '''

    :return:
    :rtype:
    '''

    # TODO: move this to markdown file.  Could store in pages folder and access by dictionary?
    markdown_text = '''
    If you are not familiar with this area: 
    '''

    google_link = r'https://www.google.com/maps/@38.740792,-123.0507687,13z/data=!5m1!1e4?entry=ttu&g_ep=EgoyMDI1MDIwNS4xIKXMDSoASAFQAw%3D%3D'

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
                # html.Hr(),

                # dcc.Markdown([markdown_text]),
                html.A([dbc.Button('open GoogleMaps\nLake Sonoma', )], href=google_link, target='_blank',
                       className='ml-10 mr-10'),
            ])
        )
    ])


def draw_scatter_all_LS_runs():
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                              html.Div([ dcc.Markdown('* Hover over a run to show on map.\n* Click on a run to show on 3D topographic plot.'),
                                        #html.H5('all run activities')
                                       ],style={'display': 'inline-block', 'vertical-align': 'top'},),
                              ]),
                    html.Br(),
                    html.Div([
                    dcc.Loading(dcc.Graph(id='plot_all_lake_sonoma_runs',
                                          figure=px.scatter(df_all_LS_runs,
                                                            x='start_date',
                                                            #y='distance_miles',
                                                            y='distance',
                                                            # color='total_elevation_gain_miles',
                                                            # size='total_elevation_gain_miles',
                                                            color='total_elevation_gain',
                                                            size='total_elevation_gain',
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
                                                            title='all Lake Sonoma run activities'

                                                            )#.update_layout(title_x=0.5, autosize=True),
                                                            .update(layout_coloraxis_showscale=False)
                                                            .update_layout(
                                                                # title='all runs',
                                                                title_x=0.5,
                                                                autosize=True,
                                                                showlegend=False,
                                                                hovermode='closest',

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
                    # dbc.Modal([
                    #     dbc.ModalHeader(dbc.ModalTitle("plot controls")),
                    #     dbc.ModalBody([modal_help_run_selection]),
                    #     # dbc.ModalFooter(dbc.Button('close',
                    #     #                            id='btn_close_plot_help',
                    #     #                            className='ms-auto',
                    #     #                            n_clicks=0))
                    # ], id='modal_plot_help', is_open=False, ),
                ], ),
            )
        ],
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
                                       'zIndex': 1,  # seems like I have to set this z order manually to be a low value or else it rises all the way to top
                                       # this is color or background on dark tile theme above
                                       # determined by color picker on screen
                                       'background':'#262626'}
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

def draw_topo_lake_sonoma_with_placeholder_run():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dcc.Loading([
                        dcc.Graph(figure=fig,
                                  id='topo_plot_lake_sonoma',
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
    ''' return index of nums array closest to target value
        nums array is sorted
    '''
    l, r = 0, len(nums) - 1
    l_prev, r_prev = -99, -99

    # <= comparison allows values outside the array (edge case is smaller values) to be tested
    # if you only use <   then you'd have to have a return statement outside while-loop
    while l <= r:
        # base case: we are now at closest point
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
            # dont mid + 1 here or on the left ptr.  we want to find closest but cant tell here if
            # we are closer to edges or mid.  so keep mid in both cases
            r = mid
        else:
            l = mid
    # no return here since this will exit inside while looo


@callback(Output('selected_run_lake_sonoma','positions'),

          Input('plot_all_lake_sonoma_runs', 'hoverData'),
          # State('topo_plot_lake_sonoma', 'figure'),
          config_prevent_initial_callbacks=True)
def display_hover_data(hover_data):
    # pp(hover_data)
    start_date = hover_data['points'][0]['x']
    distance = hover_data['points'][0]['y']
    run_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    mask = (df_all_LS_runs['start_date'] == run_date) & (df_all_LS_runs['distance']==distance)
    summary_points = df_all_LS_runs[mask]['map.summary_polyline'].values[0]

    leaflet_format = polyline_to_dash_leaflet(summary_points)

    return leaflet_format  #, new_figure


# Callback to capture click event on scatter plot
@callback(Output('topo_plot_lake_sonoma', 'figure'),
    Input('plot_all_lake_sonoma_runs', 'clickData'),
    config_prevent_initial_callbacks=True)
def display_click_data(click_data):
    if click_data:
        # return f"You clicked on: {click_data['points'][0]['x']}, {click_data['points'][0]['y']}"

        start_date = click_data['points'][0]['x']
        distance = click_data['points'][0]['y']
        run_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        mask = (df_all_LS_runs['start_date'] == run_date) & (df_all_LS_runs['distance'] == distance)
        summary_points = df_all_LS_runs[mask]['map.summary_polyline'].values[0]

        lats, lons, = polyline_to_lats_lons(summary_points)
        lons_idx = [binary_search_find_closest_idx(xi, x) for x in lons]
        lats_idx = [binary_search_find_closest_idx(yi, y) for y in lats]

        lons_adjusted = [xi[x] for x in lons_idx]
        lats_adjusted = [yi[y] for y in lats_idx]
        elevations = [float(Z[z[0]][z[1]]) for z in zip(lats_idx, lons_idx)]
        df_specific_run = pd.DataFrame({'latitude': lats_adjusted, 'longitude': lons_adjusted, 'elevation': elevations})

        # pp(figure)

        # figure_data_surface = figure[0]
        # figure_data_new_run = go.Scatter3d(x=df_specific_run['longitude'],
        #                            y=df_specific_run['latitude'],
        #                            z=df_specific_run['elevation'],
        #                            mode='lines+markers',
        #                            name='aasdf',
        #                            marker=dict(size=3, color='red'))

        new_figure = go.Figure(go.Surface(x=xi, y=yi, z=Z,
                                          surfacecolor=Z_water,
                                          opacity=0.7,
                                          ),
                               )

        new_figure.update_traces(contours_z=dict(show=False,
                                                 usecolormap=False,
                                                 highlightcolor="darkslategrey",
                                                 # project_z=True
                                                 )
                                 )
        new_figure.update_layout(title=dict(text='Lake Sonoma - low resolution plot... for now'),
                                 scene=dict(xaxis_title='Longitude',
                                            yaxis_title='Latitude',
                                            zaxis_title='Elevation (m)',
                                            aspectmode='manual',
                                            aspectratio=dict(x=1.5, y=1.2, z=0.5),  #
                                            ),
                                 autosize=True,
                                 # scene_camera_eye=dict(x=1.87, y=0.88, z=-0.4),
                                 # width=1200,
                                 height=900,
                                 # margin=dict(l=65, r=50, b=65, t=90)
                                 template='plotly_dark',
                                 hovermode=False,
                                 )
        new_figure.add_trace(go.Scatter3d(x=df_specific_run['longitude'],
                                          y=df_specific_run['latitude'],
                                          z=df_specific_run['elevation'],
                                          mode='lines+markers',
                                          # name='2024 LS100K',
                                          marker=dict(size=3, color='red')))
        return new_figure
    else:
        raise PreventUpdate



def layout():
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
            draw_topo_lake_sonoma_with_placeholder_run()
        ],  className='mt-3'),  # xs=12, sm=12, md=6, lg=6, xl=6,
    ], )   # className='mb-4 mt-2 align-items-end'

    markdown_text = ''''''
    layout_notes = dbc.Row([
        dbc.Col([
            dcc.Markdown([markdown_text]),
        ],  className='mt-3'),  # xs=12, sm=12, md=6, lg=6, xl=6,
    ], )   #

    layout_lake_sonoma = [
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