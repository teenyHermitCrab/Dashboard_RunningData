import dash
from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
import Assets.file_paths as fps
from Pages.sidebar import sidebar

pd.options.mode.chained_assignment = None  # default='warn'


df_pickle_filepath = fps.page_statistics_runs_df_pickle_path
df_all_names_scrubbed = pd.read_pickle(df_pickle_filepath)


def draw_year_range_select():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                             html.P('select year range (all plots)'),
                             dcc.RangeSlider(id='range_select_years',
                                             min=2015, max=2025, step=1,
                                             marks={i: str(i) for i in range(2015, 2026)},
                                             value=[2017, 2024],
                                            ),
                             ], xs=12, sm=10, md=8, lg=8, xl=6),
                ]),
                html.Br(),
                html.Hr(),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                             html.P('select data for histogram, box, and cumulative plots'),
                             dcc.RadioItems(id='rbtn_data_selection',
                                            options=[' distance (miles)', ' elevation gain (miles)', ' duration'],
                                            value=' distance (miles)', ),]),
                ]),
           ])
        )
    ])


def draw_histogram_from_yearly_breakdown():
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Loading(dcc.Graph(id="statistics_histogram_plot_range_select", style={'display':'none'}, ),
                                type="cube",
                                delay_show=500,
                                overlay_style={'visibility':'visible', 'filter':'blur(3px)'},
                                ),
                ])
            )
        ])


def draw_box_plot_from_yearly_selection():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Loading(dcc.Graph(id="box_plot_yearly", style={'display': 'none'}, ),
                            type="cube",
                            delay_show=500,
                            overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'},
                            ),
                # html.Br(),
            ])
        )
    ])


def draw_line_plot_cumulative_data():
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Loading(dcc.Graph(id="line_plot_cumulative", style={'display': 'none'}, ),
                                type="cube",
                                delay_show=500,
                                overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'},
                                ),
                    # html.Br(),
                ])
            )
        ])




categories_yaxis = ['total_elevation_gain_miles', 'elevation_gain_per_mile', 'pace_moving_time', 'pace_elapsed_time']  # add calories when that data is incorporated

def draw_categories_scatter():
    return html.Div([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Div(
                                        'select Y axis data:'
                                    ),
                                    html.Div(
                                        dcc.Dropdown(id='dropdown_scatter_yaxis',
                                                     options=[{'label': i, 'value': i} for i in categories_yaxis],
                                                     value=categories_yaxis[1]),
                                        #style = {'width': '25%', }
                                        #className="dash-bootstrap"
                                    ),
                                    html.Br(),
                                    dcc.Loading(
                                        dcc.Graph(id="scatter_user_selected_categories", style={'display': 'none'}, ),
                                        type="cube",
                                        delay_show=500,
                                        overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'},
                                    ),
                                ]),
                            ],)
                        ])
    ])


def draw_correlation_heatmap():
    return html.Div([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    dcc.Graph(id="heatmap_correlation", style={'display': 'none'}, ),
                                    type="cube",
                                    delay_show=500,
                                    overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'},
                                ),
                            ],)
                        ])
    ])



@callback(Output("statistics_histogram_plot_range_select", "figure"),
              Output('statistics_histogram_plot_range_select', 'style'),
              Output('box_plot_yearly', 'figure'),
              Output('box_plot_yearly', 'style'),
              Input("range_select_years", 'value'),
              Input('rbtn_data_selection', 'value'))
def update_data_range_plots(range_selections, rbtn_selection):
    '''

    :param range_selections:
    :type range_selections:
    :param rbtn_selection:
    :type rbtn_selection:
    :return:
    :rtype:
    '''
    start_year,stop_year = range_selections[0], range_selections[1]
    # selected_year = range_selection
    df_selected_years = df_all_names_scrubbed.loc[(df_all_names_scrubbed['year'] >= start_year) & (df_all_names_scrubbed['year'] <= stop_year)]
    # df_selected_years = df_all_names_scrubbed.loc[(df_all_names_scrubbed['year'] == selected_year)]

    column_name = {' distance (miles)': 'distance_miles',
                   ' elevation gain (miles)': 'total_elevation_gain_miles',
                   ' duration': 'elapsed_time'}

    histogram = px.histogram(
                df_selected_years,
                x='month',
                y=column_name[rbtn_selection],
                category_orders=dict(month=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']),
                #animation_frame="year",
                range_x=[-1,12],
                #range_y=[0, 30],
                labels={'total_elevation_gain_miles': 'elevation gain (miles)',
                        'elapsed_time':'elapsed time',
                        'month':'',
                        'distance_miles':'distance (miles)',
                        },
                template='plotly_dark',
            ).update_yaxes(autorange=True,fixedrange = False)

    boxplot = px.box(df_selected_years,
                     x='month',
                     y=column_name[rbtn_selection],
                     notched=False,
                     category_orders=dict(month=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']),
                     #animation_frame="year",
                     range_x=[-1,12],
                     points=False,

                     #range_y=[0, 30],
                     labels={'total_elevation_gain_miles': 'elevation gain (miles)',
                             'elapsed_time':'elapsed time',
                             'distance_miles':'distance (miles)',
                             'month':''},
                     template='plotly_dark',).update_yaxes(autorange=True,fixedrange = False)
    return (
            histogram, {'display':'block', },
            boxplot, {'display': 'block', },
    )



@callback(Output('line_plot_cumulative', 'figure'),
          Output('line_plot_cumulative', 'style'),
          Input("range_select_years", 'value'),
          Input('rbtn_data_selection', 'value'))
def update_cumulative_plot(range_selections, rbtn_selection):
    column_name = {' distance (miles)': 'distance_miles',
                   ' elevation gain (miles)': 'total_elevation_gain_miles',
                   ' duration': 'elapsed_time'}
    target_data = column_name[rbtn_selection]

    start_year, stop_year = range_selections[0], range_selections[1]
    # selected_year = range_selection
    df_selected_years = df_all_names_scrubbed.loc[(df_all_names_scrubbed['year'] >= start_year) & (df_all_names_scrubbed['year'] <= stop_year)]
    # df_selected_years = df_all_names_scrubbed.loc[(df_all_names_scrubbed['year'] == selected_year)]

    df_selected_years.loc[:,'cumulative'] = df_selected_years[target_data].cumsum()

    fig = px.line(df_selected_years,
                  x='start_date',
                  y='cumulative',
                  labels={'total_elevation_gain_miles': 'elevation gain (miles)',
                          'elapsed_time': 'elapsed time',
                          'month': '',
                          'start_date': '',
                          'cumulative': f'cumulative {rbtn_selection}'},
                  template='plotly_dark'
                  )
    return fig, {'display': 'block'}





@callback(Output('scatter_user_selected_categories', 'figure'),
          Output('scatter_user_selected_categories', 'style'),
          Output('heatmap_correlation', 'figure'),
          Output('heatmap_correlation', 'style'),
          Input('dropdown_scatter_yaxis', 'value'),
          Input("range_select_years", 'value'),
          )
def update_scatter_heatmap(y_axis_selection, range_selections):
    start_year, stop_year = range_selections[0], range_selections[1]
    # selected_year = range_selection

    df_selected_years = df_all_names_scrubbed.loc[(df_all_names_scrubbed['year'] >= start_year) &
                                                  (df_all_names_scrubbed['year'] <= stop_year)]

    fig_scatter = px.scatter(df_selected_years,
                             x='distance_miles',
                             y=y_axis_selection,
                             template='plotly_dark',
                             hover_name='name',
                             hover_data=['start_date', y_axis_selection,],
                             trendline='lowess',  # ols lowess
                             trendline_color_override="red",
                             labels={'total_elevation_gain_miles':'elevation gain (miles)',
                                     'elevation_gain_per_mile':'elevation gain per mile',
                                     'pace_moving_time':'pace - moving time',
                                     'pace_elapsed_time':'pace - elapsed time',
                                     'distance_miles': 'distance (miles)',
                                     },
                             )

    # if y_axis_selection == 'pace_moving_time':
    #     #  lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
    #     fig_scatter.update_layout(yaxis_tickformat=lambda x: f"{int(x // 60)}:{int(x % 60):02d}")

    columns_to_keep = categories_yaxis[:]
    columns_to_keep.extend(['distance_miles',])
    # this chaining warning has been disabled (see import and warning call on line 18)
    df_selected_years = df_selected_years.loc[:, columns_to_keep]

    df_corr = df_selected_years.corr()
    mask = np.triu(np.ones_like(df_corr, dtype=bool))
    df_mask = df_corr.mask(mask)

    # This iteration is to remove upper triangle, to keep display info off of page
    # Is there a pandas way of doing this rather than iteration?
    # Feels like a better way would be to somehow disable the display in a layout or trace option
    rows, columns = df_corr.shape
    idx_clear = 0
    for row in range(rows):
        for column in range(columns):
            if column >= idx_clear:
                with warnings.catch_warnings():
                    warnings.simplefilter(action='ignore', category=FutureWarning)
                    # Warning-causing lines of code here
                    df_corr.iloc[row,column] = ''   # this will be displayed, so empty string is good.  np.nan if this was a numpy array?
        idx_clear += 1

    fig_correlation = go.Figure()
    fig_correlation.add_trace(
        go.Heatmap(
            x=df_corr.columns,
            y=df_corr.index,
            z=df_mask,
            text=df_corr.values,
            texttemplate='%{text:.2f}',
            colorscale='viridis',
        )
    )
    fig_correlation.update_layout(title='correlation heatmap',
                                  title_x=0.5,
                                  yaxis_autorange='reversed',
                                  )
    fig_correlation.layout.template = 'plotly_dark'


    return fig_scatter, {'display': 'block'}, fig_correlation, {'display': 'block'}







def layout():
    layout_histo_box = dbc.Row([
            dbc.Col([
                draw_histogram_from_yearly_breakdown()
            ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3'),
            dbc.Col([
                draw_box_plot_from_yearly_selection()
            ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3'),
        ], className='mb-4 mt-2 align-items-end')

    layout_cumulative = dbc.Row([
            dbc.Col([
                draw_line_plot_cumulative_data()
            ], ),   #xs=12, sm=12, md=12, lg=11, xl=10, className='mt-3'
        ], className='justify-content-center')

    layout_scatter_and_heatmap = dbc.Row([
            dbc.Col([
                draw_categories_scatter()
            ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3'),
            dbc.Col([
                draw_correlation_heatmap()
            ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3'),
        ], className='mb-4 mt-2 align-items-end')



    layout_statistics = [
        sidebar(__name__),
        html.Div([
            dbc.Container(draw_year_range_select(), fluid=True),
            dbc.Container(layout_histo_box, fluid=True ),
            dbc.Container(layout_cumulative, fluid=True),
            dbc.Container(layout_scatter_and_heatmap, fluid=True)
        ], className='content')
    ]

    return layout_statistics