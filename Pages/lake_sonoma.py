import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import Assets.file_paths as fps
from Pages.sidebar import sidebar


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

xi = np.linspace(x.min(), x.max(), 200)
yi = np.linspace(y.min(), y.max(), 200)

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

fig = go.Figure(go.Surface(x=xi,y=yi,z=Z,
                           surfacecolor=Z_water,
                           ),
                )


fig.update_traces(contours_z=dict(show=False,
                                  usecolormap=False,
                                  highlightcolor="limegreen",
                                  project_z=True
                                  )
                  )
fig.update_layout(title=dict(text='Lake Sonoma test - 2024 100K'),
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
    **This page is under development**  - will add ability to select all runs in Lake Sonoma area. Using this 100K run as a placeholder.
    * Note there are slight elevation errors on red trace projected onto 3D surface.  (No, I can't fly or burrow underground...) 
        * When recording a run, my GPS watch will always have an error range. 
        * The topographic data was retrieved from NOAA at a relatively coarse resolution.
        * Further data-processing will be done to match latitude/longitude of run data to topographic elevation data.
    
    If you are not familiar with this area: 
    '''

    google_link = r'https://www.google.com/maps/@38.740792,-123.0507687,13z/data=!5m1!1e4?entry=ttu&g_ep=EgoyMDI1MDIwNS4xIKXMDSoASAFQAw%3D%3D'

    return html.Div([
        dbc.Card(
            dbc.CardBody([
                # TODO: could make this list dynamic, based on which files match regex pattern
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
                html.Br(),
                html.Hr(),

                dcc.Markdown([markdown_text]),
                html.A([dbc.Button('open GoogleMaps\nLake Sonoma', )], href=google_link, target='_blank',
                       className='ml-10 mr-10'),
            ])
        )
    ])


def draw_topo_lake_sonoma_with_placeholder_run():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dcc.Loading([
                        dcc.Graph(figure=fig, config={'displaylogo': False})
                    ]),
                ]),
            ])
        )
    ])



def layout():
    layout_components_photos = dbc.Row([
        dbc.Col([
            draw_photos()
        ], className='mt-3'),  # xs=12, sm=12, md=12, lg=11, xl=10, className='mt-3'
    ], )   # className='justify-content-center'

    layout_components_topo = dbc.Row([
        dbc.Col([
            draw_topo_lake_sonoma_with_placeholder_run()
        ],  className='mt-3'),  # xs=12, sm=12, md=6, lg=6, xl=6,
    ], )   # className='mb-4 mt-2 align-items-end'


    layout_lake_sonoma = [
        sidebar(__name__),
        html.Div([
            # layout_components_scatter
            dbc.Container(layout_components_photos, fluid=True, ),
            dbc.Container(layout_components_topo, fluid=True)
        ], className='content')
    ]

    return layout_lake_sonoma