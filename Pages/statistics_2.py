import base64
from datetime import datetime
import dash
from dash import dcc, html, callback, Input, Output, Patch, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from pprint import pprint as pp
import re
import Assets.file_paths as fps
from Pages.data import df_all_runs
from Pages.sidebar import sidebar

# pd.options.mode.chained_assignment = None  # default='warn'


def layout():
    layout_components_scatter = dbc.Row([
        dbc.Col([
            draw_scatter_all_runs(),
        ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3 d-flex flex-column' ),
        dbc.Col([
            draw_category_select(),
            draw_line_plot_cumulative_data(),
        ], xs=12, sm=12, md=6, lg=6, xl=6, className='mt-3 d-flex flex-column' ),
    ], className='justify-content-center d-flex align-items-stretch')

    layout_cumulative_images = dbc.Row([
        dbc.Col([
            draw_images_cumulative_data()
        ], ),  # xs=12, sm=12, md=12, lg=11, xl=10, className='mt-3'
    ], className='justify-content-center')

    layout_statistics = [
        dcc.Store(id='store_stats2_page_load_trigger', data={'loaded': False}),
        dcc.Store(id='store_stats2_data', data={}),

        sidebar(__name__),
        html.Div([
            dbc.Container(layout_components_scatter,  fluid=True,),
            dbc.Container(layout_cumulative_images, fluid=True),
        ], className='content'),
    ]

    return layout_statistics




# Callback to trigger once when the page loads
@callback(
    Output('scatter_stats2_all_runs', 'figure'),
    Output("store_stats2_page_load_trigger", "data"),
    Output('store_stats2_data', 'data'),
    Input("store_stats2_page_load_trigger", "data"),
    State('dropdown_stats2_category_select', 'value'),
    # State('storage_df_all_runs', 'data', ),

    prevent_initial_call="initial_duplicate"  # Ensures it only runs once after initial render
)
def on_page_load(store_data, category_selection):
    if not store_data.get("loaded"):  # Check if page has already loaded
        # df_all_runs = pd.DataFrame(all_run_data)

        figure = px.scatter(df_all_runs,
                            x='start_date',
                            y='distance_miles',
                            #y='distance',
                            color='total_elevation_gain_miles',
                            size='total_elevation_gain_miles',
                            # color='total_elevation_gain',
                            # size='total_elevation_gain',
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
                            title='all runs',
                            )
        figure.update_layout(title_x=0.5,
                             autosize=True,
                             dragmode=None,
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
        figure.update_layout(coloraxis_showscale=False)



        column_name = {'blood': 'volume_blood_liters',
                       'respiration': 'volume_respiration_liters',
                       'elevation': 'total_elevation_gain_miles'}
        units = {'blood': 'liters',
                 'respiration': 'liters',
                 'elevation': 'miles'}
        target_data = column_name[category_selection]
        df_all_runs.loc[:, 'cumulative'] = df_all_runs[target_data].cumsum()


        title, units, cumulative_value_formatted, description, category = '', '', '', '', ''
        # no need to hunt through the figure, we have the dataFrame.
        run_count = len(df_all_runs)
        if run_count > 0:
            cumulative_value = df_all_runs['cumulative'].iloc[-1]
        else:
            cumulative_value = 0

        match category_selection:
            case 'blood':
                title = '## Total Blood Volume'
                units = 'liters'
                cumulative_value_formatted = f'{cumulative_value:,.0f}'
                description = fr'estimated cumulative volume of blood pumped by my ticker over **{run_count:,}** runs.'
                category = 'Blood'
            case 'respiration':
                title = '## Total Respiration Volume'
                units = 'liters'
                cumulative_value_formatted = f'{cumulative_value:,.0f}'
                description = fr'estimated cumulative volume of air huffed and puffed over **{run_count:,}** runs.'
                category = 'Respiration'
            case 'elevation':
                title = '## Total Elevation Gain'
                units = 'miles'
                cumulative_value_formatted = f'{cumulative_value:,.1f}'
                description = fr'cumulative elevation gain over **{run_count:,}** runs.'
                category = 'Elevation'
            case _:
                'unknown selection'
        md_text = f'{title}\n---\n### **{cumulative_value_formatted}** {units}\n{description}'

        this_page_data = {
            'start_date': df_all_runs.iloc[0]['start_date'],
            'stop_date': df_all_runs.iloc[-1]['start_date'],
            'markdown_description': md_text,
            'category': category,
            'cumulative_value': cumulative_value,
            'units': units,
        }

        return figure, {'loaded':True}, this_page_data
    return dash.no_update, dash.no_update, dash.no_update  # Prevent unnecessary updates




#region modal plot help

# TODO: move this to static files or file in pages folder
text_modal_help = '''
* Pan or zoom the plot using range slider handles or plot buttons.
* Cumulative line plot will automatically update.
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


@callback(Output("stats2_modal_plot_help", "is_open"),
          Input("btn_stats2_open_plot_help", "n_clicks"),
          # Input("btn_close_plot_help", "n_clicks"),
          State("stats2_modal_plot_help", "is_open"))
def toggle_modal_plot_help(n1, is_open):
    if n1:
        return not is_open
    return is_open
#endregion



#region modal explain estimates
modal_stats2_explain_estimates = html.Div([
        dbc.Select(id='dropdown_stats2_modal_explain_category',
                   options=[
                       {'label': 'blood volume 🩸', 'value': 'blood'},
                       {'label': 'respiration volume 💭', 'value': 'respiration'},
                       {'label': 'elevation ✈️', 'value': 'elevation'},
                       {'label': 'calories 🍇', 'value': 'calories'},

                   ],
                   value='blood',
                   style={'width':'auto'}),
        html.Hr(),
        dcc.Markdown(id='markdown_stats2_explain_category', mathjax=True),
        ])


@callback(
    Output('markdown_stats2_explain_category', 'children'),
    Input('dropdown_stats2_modal_explain_category', 'value')
)
def update_markdown_explain_category(selected_value):
    markdown_file_path =''
    match selected_value:
        case 'blood':
            markdown_file_path = fps.page_statistics2_explain_estimate_blood_path
        case 'respiration':
            markdown_file_path = fps.page_statistics2_explain_estimate_respiration_path
        case 'elevation':
            markdown_file_path = fps.page_statistics2_explain_estimate_elevation_path
        case 'calories':
            markdown_file_path = fps.page_statistics2_explain_estimate_calories_path
        case _:
            raise Exception('invalid selection for explain estimates')

    markdown = ''
    with open(markdown_file_path) as f:
        markdown = f.read()

    return markdown




@callback(Output("stats2_modal_estimate_explanation", "is_open"),
          Input("btn_stats2_explain_estimate", "n_clicks"),
          # Input("btn_close_plot_help", "n_clicks"),
          State("stats2_modal_estimate_explanation", "is_open"))
def toggle_modal_estimate_explanation(n1, is_open):
    if n1:
        # might need to adjust markup here
        return not is_open
    return is_open
#endregion




markdown_scatter_plot = '''
Select date range by adjusting scatter plot window.
'''

def draw_scatter_all_runs():
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                              html.Div([
                                        dcc.Markdown([markdown_scatter_plot]),
                                       ],style={'display': 'inline-block', 'vertical-align': 'top'},),
                              html.Div([
                                  dbc.Button([
                                                        #html.I(className="fa-regular fa-circle-question me-3 fa-1x"),
                                                        '  help'
                                                     ],
                                                   id='btn_stats2_open_plot_help', n_clicks=0)
                              ],
                                className='float-end',
                                # style={'display': 'inline-block', 'vertical-align': 'top'},
                                title='click to display plot control help',),
                              ]),
                    html.Br(),
                    html.Div([
                    dcc.Loading(dcc.Graph(id='scatter_stats2_all_runs',
                                          figure = px.scatter(pd.DataFrame(), title='loading data...', template='plotly_dark'),
                                          # default double-click is really fast, don't show plotly logo
                                          config={'doubleClickDelay':750, 'displaylogo': False},
                                          ), className='h-100',
                                             type="cube",
                                             delay_show=500,
                                             overlay_style={'visibility': 'visible', 'filter': 'blur(3px)',},
                                ),
                    ]),
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle("plot controls")),
                        dbc.ModalBody([modal_help_run_selection]),
                        # dbc.ModalFooter(dbc.Button('close',
                        #                            id='btn_close_plot_help',
                        #                            className='ms-auto',
                        #                            n_clicks=0))
                    ], id='stats2_modal_plot_help', is_open=False, ),
                ], ),
            )
        ],
    )

def draw_category_select():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Br(),
                dbc.Row([
                    dbc.Col(html.Div([html.P('select category: '),
                            ]), width= 'auto', className="text-left"),
                    dbc.Col(html.Div([
                                dbc.Select(id='dropdown_stats2_category_select',
                                           options=[
                                                   {'label': 'blood volume 🩸',       'value': 'blood'},
                                                   {'label': 'respiration volume 💭', 'value': 'respiration'},
                                                   {'label': 'elevation ✈️',          'value': 'elevation'},
                                                   # {'label': 'calories 🍇',           'value': 'calories', 'disabled': 'True'},
                                           ],
                                           value='blood',
                                           style={'width': 'auto'}
                                           )
                                     ]), width='auto', className="text-left"
                             ),
                ]),
           ])
        )
    ])

def draw_line_plot_cumulative_data():
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.P('Click on plot line to update calculation for that point.',
                               className='d-flex justify-content-center'),
                                dcc.Loading(dcc.Graph(id="line_plot_stats2_cumulative",
                                                      style={'display': 'none',
                                                             'height': '23.5rem'},
                                                      config={'displayModeBar': False,  # Hide the mode bar
                                                             }
                                                      ),
                                            type="cube",
                                            delay_show=500,
                                            overlay_style={'visibility': 'visible', 'filter': 'blur(3px)'},
                                            ),
                                ], style={'position': 'relative',
                                          'width': 'auto',
                                          'margin': 'auto',
                                          'padding-bottom': '40px'
                                          }
                    ),


                    # dbc.Row([
                    #     dbc.Col([
                    #         # dcc.Slider(id= 'sldr_stats2_choose_point')
                    #     ]),
                    # ]),
            ])
        )
    ])

def b64_image(image_filename, image_format):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return f'data:image/{image_format};base64,' + base64.b64encode(image).decode('utf-8')


def draw_images_cumulative_data():
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([

                                dbc.Col([
                                    dbc.Row([dcc.Markdown(id='markdown_cumulative_description', dangerously_allow_html=True),]),
                                    html.Br(),
                                    html.Br(),
                                    dbc.Row([dbc.Button('explain estimate',
                                                        id='btn_stats2_explain_estimate',
                                                        style={'width':'auto'},
                                                        className='m-3'),]),
                                ], xs=12, sm=12, md=5, lg=5, xl=5, className='mt-3'),

                                dbc.Col([
                                    dbc.Row([
                                        dbc.Col([html.Img(id='image_stats2_stick_figure', style={'width': '70%', 'height': 'auto', 'float':'right'}),
                                        ], className='mt-3'),

                                        dbc.Col([html.Img(id='image_stats2_equivalent_volume',
                                                                  style={'width': '100%',
                                                                 'height': 'auto%',
                                                                 'border': '2px solid black',
                                                                 # Border thickness and color
                                                                 'padding': '5px',
                                                                 # Optional: padding inside the border
                                                                 'border-radius': '5px'  # Optional: rounded corners
                                                                 }),
                                                         dcc.Markdown(id='markdown_stats2_equivalent_to',
                                                                      dangerously_allow_html=True),





                                                         # dbc.Row([
                                                         #     dbc.Col(html.Div([dcc.Markdown(id='markdown_stats2_equivalent_to', dangerously_allow_html=True),],
                                                         #                      style={'whiteSpace': 'nowrap'}, ),
                                                         #             width='auto',
                                                         #             style={'flex': '0 0 auto'}),
                                                         # ]),
                                                ], className='mt-3'),
                                    ],),

                                ], xs=12, sm=12, md=5, lg=5, xl=5, className='mt-3'),

                                dbc.Col([], xs=12, sm=12, md=2, lg=2, xl=2),

                            ], className='mb-4 mt-2'),  # align-items-end

                            dbc.Modal([
                                dbc.ModalHeader(dbc.ModalTitle("How are these values derived?")),
                                dbc.ModalBody([modal_stats2_explain_estimates]),

                            ],  id='stats2_modal_estimate_explanation',
                                is_open=False,
                                size='lg',
                            ),
                        ])
                    ),
                ])
        )
    ])



@callback(Output('line_plot_stats2_cumulative', 'figure', allow_duplicate= True),
          Output('line_plot_stats2_cumulative', 'style', allow_duplicate=True),
          Output('store_stats2_data', 'data', allow_duplicate = True),

          Input('scatter_stats2_all_runs', 'relayoutData'),
          State('dropdown_stats2_category_select', 'value'),
          State('scatter_stats2_all_runs', 'figure'),
          # State('storage_df_all_runs', 'data'),
          config_prevent_initial_callbacks=True,)
def display_selected_runs_on_cumulative_plot(relay_out_data: dict, dropdown_selection, figure):
    # df_all_runs = pd.DataFrame(all_runs_data)

    if not relay_out_data or not figure:
        raise PreventUpdate

    '''
    Yah.. this looks like a mess, but there doesn't seem to be a way to detect mouse-up events. 
    Maybe there is a javascript way to do this. or a different dash library to use.
    But until I find that, I have to pull the displayed range off of relayoutData or from figure
    Hmmm... should probably just do this from figure.

    The problem with this callback is that it updates frequently while graph is being changed, so there is alot 
    of traffic.  Need to find that mouse up event 
    '''
    initial_page_load = relay_out_data == {'autosize': True}
    range_slider_was_directly_adjusted = 'xaxis.range' in relay_out_data
    range_slider_modified_on_plot_or_zoom_buttons = 'xaxis.range[0]' in relay_out_data and 'xaxis.range[1]' in relay_out_data
    plot_buttons = 'xaxis.autorange' in relay_out_data or 'autosize' in relay_out_data

    start_date, end_date = None, None
    # print(f'{relay_out_data = }')

    if range_slider_was_directly_adjusted:  # this is where slider bars are used to adjust view
        # print('directly adjusted')
        start_date = datetime.strptime(relay_out_data['xaxis.range'][0], '%Y-%m-%d %H:%M:%S.%f').date()
        stop_date = datetime.strptime(relay_out_data['xaxis.range'][1], '%Y-%m-%d %H:%M:%S.%f').date()
        # start_date = relay_out_data['xaxis.range'][0]
        # stop_date = relay_out_data['xaxis.range'][1]
        # msg = f'AA  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
        # print(msg, flush=True)
    elif range_slider_modified_on_plot_or_zoom_buttons:  # this is where the plot itself is dragged: pan or zoom
        # print('plot or zoom on plot itself')
        start_date = datetime.strptime(relay_out_data['xaxis.range[0]'], '%Y-%m-%d %H:%M:%S.%f').date()
        stop_date = datetime.strptime(relay_out_data['xaxis.range[1]'], '%Y-%m-%d %H:%M:%S.%f').date()
        # start_date = relay_out_data['xaxis.range[0]']
        # stop_date = relay_out_data['xaxis.range[1]']
        # msg = f'BB  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
        # print(msg, flush=True)
    elif initial_page_load:
        start_date = df_all_runs.iloc[0]['start_date']
        stop_date = df_all_runs.iloc[-1]['start_date']
    else:  # 'xaxis.autorange' in relay_out_data or 'autosize' in relay_out_data:
        print('button controls')
        # plot control buttons pressed or axis reset
        start_date = datetime.strptime(figure['layout']['xaxis']['range'][0], '%Y-%m-%d %H:%M:%S.%f').date()
        stop_date = datetime.strptime(figure['layout']['xaxis']['range'][1], '%Y-%m-%d %H:%M:%S.%f').date()
        # start_date = figure['layout']['xaxis']['range'][0]
        # stop_date = figure['layout']['xaxis']['range'][1]
        # msg = f'BB  {relay_out_data = }\n  {start_date = },   {stop_date = },  {type(start_date) = }'
        # print(msg, flush=True)

    # print(f'{start_date = }  {stop_date = }')

    mask = (df_all_runs['start_date'] >= start_date) & (df_all_runs['start_date'] <= stop_date)
    df_date_range = df_all_runs[mask]

    # print(len(df_date_range))

    column_name = {'blood': 'volume_blood_liters',
                   'respiration': 'volume_respiration_liters',
                   'elevation': 'total_elevation_gain_miles'}
    units = {'blood': 'liters',
             'respiration': 'liters',
             'elevation': 'miles'}
    target_data = column_name[dropdown_selection]
    df_date_range.loc[:, 'cumulative'] = df_date_range[target_data].cumsum()

    fig_line = px.line(df_date_range,
                  x='start_date',
                  y='cumulative',
                  labels={'total_elevation_gain_miles': 'total elevation gain (miles)',
                          'elapsed_time': 'elapsed time\n seconds',
                          'month': '',
                          'start_date': '',
                          'cumulative': f'cumulative {dropdown_selection}<br>{units[dropdown_selection]} '},
                  template='plotly_dark',
                  hover_data = {'start_date': False,
                                'cumulative':':,.0f'},  # add comma separator(s), no need to show decimal places
                  )
    fig_line.update_layout(hoverdistance=30,
                           dragmode=False,
                           clickmode='event+select',
                           )
    fig_line.add_shape(
        go.layout.Shape(
            type="line",
            x0=df_date_range['start_date'].max(), x1=df_date_range['start_date'].max(),
            y0=df_date_range['cumulative'].min(), y1=df_date_range['cumulative'].max(),
            line=dict(color="red", width=2, dash="dash")
        )
    )


    title, units, cumulative_value_formatted, description, category = '', '', '', '', ''
    # no need to hunt through the figure, we have the dataFrame.
    run_count = len(df_date_range)
    if run_count > 0:
        cumulative_value = df_date_range['cumulative'].iloc[-1]
    else:
        cumulative_value = 0
    match dropdown_selection:
        case 'blood':
            title = '## Total Blood Volume'
            units = 'liters'
            cumulative_value_formatted = f'{cumulative_value:,.0f}'
            description = fr'estimated cumulative volume of blood pumped by my ticker over **{run_count:,}** runs.'
            category = 'Blood'
        case 'respiration':
            title = '## Total Respiration Volume'
            units = 'liters'
            cumulative_value_formatted = f'{cumulative_value:,.0f}'
            description = fr'estimated cumulative volume of air huffed and puffed over **{run_count:,}** runs.'
            category = 'Respiration'
        case 'elevation':
            title = '## Total Elevation Gain'
            units = 'miles'
            cumulative_value_formatted = f'{cumulative_value:,.1f}'
            description = fr'cumulative elevation gain over **{run_count:,}** runs.'
            category = 'Elevation'
        case _:
            'unknown selection'

    md_text = f'{title}\n---\n### **{cumulative_value_formatted}** {units}\n{description}'
    data = {
        'start_date': start_date,
        'stop_date' : stop_date,
        'markdown_description': md_text,
        'category': category,
        'cumulative_value': cumulative_value,
        'units':units,
    }

    return fig_line, {'display': 'block', 'height':'23.5rem'}, data





@callback(Output('store_stats2_data', 'data', allow_duplicate = True),
          Output('line_plot_stats2_cumulative','figure', allow_duplicate = True),
          Input('dropdown_stats2_category_select', 'value'),
          State('line_plot_stats2_cumulative', 'figure'),
          # State('store_stats2_data', 'data'),
          # State('storage_df_all_runs', 'data'),
          config_prevent_initial_callbacks=True,)
def translate_cumulative_category_select(dropdown_selection, cumulative_line_plot_figure):
    # df_all_runs = pd.DataFrame(all_runs_data)

    # when selecting a new category, redraw the figure to new data, data range
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    # Get the ID of the input that triggered the callback
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    # print()
    # print()
    # print(triggered_id)
    # pp(cumulative_line_plot_figure)

    # datetime.strptime(relay_out_data['xaxis.range'][0], '%Y-%m-%d %H:%M:%S.%f').date()

    start_date = datetime.strptime(cumulative_line_plot_figure['data'][0]['x'][0], '%Y-%m-%d').date()
    stop_date = datetime.strptime(cumulative_line_plot_figure['data'][0]['x'][-1], '%Y-%m-%d').date()
    mask = (df_all_runs['start_date'] >= start_date) & (df_all_runs['start_date'] <= stop_date)
    df_date_range = df_all_runs[mask]

    column_name = {'blood': 'volume_blood_liters',
                   'respiration': 'volume_respiration_liters',
                   'elevation': 'total_elevation_gain_miles'}
    units = {'blood': 'liters',
             'respiration': 'liters',
             'elevation': 'miles'}
    target_data = column_name[dropdown_selection]

    df_date_range.loc[:, 'cumulative'] = df_date_range[target_data].cumsum()

    fig_line = px.line(df_date_range,
                  x='start_date',
                  y='cumulative',
                  labels={'total_elevation_gain_miles': 'total elevation gain (miles)',
                          'elapsed_time': 'elapsed time\n seconds',
                          'month': '',
                          'start_date': '',
                          'cumulative': f'cumulative {dropdown_selection}<br>{units[dropdown_selection]} '},
                  template='plotly_dark',
                  hover_data={'start_date': False,
                              'cumulative': ':,.0f'},  # add comma separator(s), no need to show decimal places
                  )
    fig_line.update_layout(hoverdistance=30,
                           dragmode=False,
                           clickmode='event+select',
                           )
    fig_line.add_shape(
        go.layout.Shape(
            type="line",
            x0=df_date_range['start_date'].max(), x1=df_date_range['start_date'].max(),
            y0=df_date_range['cumulative'].min(), y1=df_date_range['cumulative'].max(),
            line=dict(color="red", width=2, dash="dash")
        )
    )

    title, units, cumulative_value_formatted, description, category = '', '', '', '', ''
    run_count, cumulative_value = 0, 0

    # TOOD: need to reset figure SO BREAK THIS UP TO ANOTHER CALLBACK
    # run_count = len(cumulative_line_plot_figure['data'][0]['x'])
    # cumulative_value = cumulative_line_plot_figure['data'][0]['y']['_inputArray'][str(run_count - 1)]
    run_count = len(df_date_range)
    if run_count > 0:
        cumulative_value = df_date_range['cumulative'].iloc[-1]
    else:
        cumulative_value = 0

    match dropdown_selection:
        case 'blood':
            title = '## Total Blood Volume'
            units = 'liters'
            cumulative_value_formatted = f'{cumulative_value:,.0f}'
            description = fr'estimated cumulative volume of blood pumped by my ticker over **{run_count:,}** runs.'
            category = 'Blood'
        case 'respiration':
            title = '## Total Respiration Volume'
            units = 'liters'
            cumulative_value_formatted = f'{cumulative_value:,.0f}'
            description = fr'estimated cumulative volume of air huffed and puffed over **{run_count:,}** runs.'
            category = 'Respiration'
        case 'elevation':
            title = '## Total Elevation Gain'
            units = 'miles'
            cumulative_value_formatted = f'{cumulative_value:,.1f}'
            description = fr'cumulative elevation gain over **{run_count:,}** runs.'
            category = 'Elevation'
        case _:
            print('UNKNOWN', dropdown_selection)
            'unknown selection'

    md_text = f'{title}\n---\n### **{cumulative_value_formatted}** {units}\n{description}'
    data = {
        'start_date': start_date,
        'stop_date': stop_date,
        'markdown_description': md_text,
        'category': category,
        'cumulative_value': cumulative_value,
        'units': units,
    }

    return data, fig_line



@callback(Output('store_stats2_data', 'data', allow_duplicate = True),
          Output('line_plot_stats2_cumulative','figure', allow_duplicate = True),
          Input('line_plot_stats2_cumulative', 'clickData'),
          State('dropdown_stats2_category_select', 'value'),
          State('store_stats2_data', 'data'),
          State('line_plot_stats2_cumulative', 'figure'),
          config_prevent_initial_callbacks=True,)
def translate_cumulative_click_data(click_data, dropdown_category_selection, store_stats2_overall_data, line_plot_figure):
    if not click_data:
        raise PreventUpdate

    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    # Get the ID of the input that triggered the callback
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    # print()
    # print(triggered_id)

    title, units, cumulative_value_formatted, description, category = '', '', '', '', ''
    run_count, cumulative_value = 0, 0

    run_count = click_data['points'][0]['pointIndex'] + 1
    cumulative_value = click_data['points'][0]['y']
    click_date = click_data['points'][0]['x']

    max_idx = len(line_plot_figure['data'][0]['x']) - 1
    max_cumulative_value = line_plot_figure['data'][0]['y']['_inputArray'][str(max_idx)]



    match dropdown_category_selection:
        case 'blood':
            title = '## Total Blood Volume'
            units = 'liters'
            cumulative_value_formatted = f'{cumulative_value:,.0f}'
            description = fr'estimated cumulative volume of blood pumped by my ticker over **{run_count:,}** runs.'
            category = 'Blood'
        case 'respiration':
            title = '## Total Respiration Volume'
            units = 'liters'
            cumulative_value_formatted = f'{cumulative_value:,.0f}'
            description = fr'estimated cumulative volume of air huffed and puffed over **{run_count:,}** runs.'
            category = 'Respiration'
        case 'elevation':
            title = '## Total Elevation Gain'
            units = 'miles'
            cumulative_value_formatted = f'{cumulative_value:,.1f}'
            description = fr'cumulative elevation gain over **{run_count:,}** runs.'
            category = 'Elevation'
        case _:
            'unknown selection'

    md_text = f'{title}\n---\n### **{cumulative_value_formatted}** {units}\n{description}'


    new_data = {
        'markdown_description': md_text,
        'category': category,
        'cumulative_value': cumulative_value,
        'units': units,
    }
    store_stats2_overall_data.update({(k,v) for k,v in new_data.items()})

    patch = Patch()
    # shapes = cumulative_figure['layout']['shapes']
    patch['layout']['shapes'] = [go.layout.Shape(type="line",
                                                 x0=click_date,
                                                 x1=click_date,
                                                 y0=0,
                                                 y1=max_cumulative_value,
                                                 line=dict(color="red", width=2, dash="dash"))
                                ]

    return store_stats2_overall_data, patch




def get_sorted_pictures(directory_path:str, units: str) -> list[dict]:
    pattern = f'^(?P<VALUE>[0-9.]+)[{units}]_(?P<DESCRIPTION>.+).(png|jpg)'
    file_data = []

    for filename in os.listdir(directory_path):
        match = re.match(pattern, filename)
        if match:
            value = match.group('VALUE')
            description_raw = match.group('DESCRIPTION')
            description = ' '.join(description_raw.split(sep='_'))
            this_data = { 'filename': filename,
                          'value': float(value),
                          'description': description
                        }
            file_data.append(this_data)

    return sorted(file_data, key=lambda x: x['value'])


def get_closest_index(picture_data, target):
    '''
    Binary search to find closest element in list, based on one of its dictionary values

    :param picture_data:
    :type picture_data:
    :param target: a value derived from estimation formula
    :type target:
    :return:
    :rtype:
    '''
    l, r = 0, len(picture_data) - 1

    # edge cases, no need to search if past endpoints
    if target <= picture_data[l]['value']:
        return l
    if target >= picture_data[r]['value']:
        return r


    prev_l, prev_r = -99, -99
    while l < r:
        if prev_l == l and prev_r == r:
            break
        prev_l, prev_r = l, r

        mid = (l + r) // 2
        candidate = picture_data[mid]['value']
        # print(f'{l=}, {r=}, {mid=}, {candidate=}')
        if candidate < target:
            l = mid
        else:
            r = mid

    #
    # after bringing the ptrs together, still must decide upon which side is closest
    l_value = picture_data[l]['value']
    r_value = picture_data[r]['value']
    diff_l = abs(l_value - target)
    diff_r = abs(r_value - target)
    if diff_l <= diff_r:
        return l
    else:
        return r


@callback(Output('markdown_cumulative_description', 'children'),
          Output('image_stats2_stick_figure', 'src'),
          Output('image_stats2_equivalent_volume', 'src'),
          Output('markdown_stats2_equivalent_to', 'children'),
          Input('store_stats2_data', 'data'),
          config_prevent_initial_callbacks=True)
def translate_cumulative_data(data):
    markdown_text = data['markdown_description']
    cumulative_value = data['cumulative_value']
    category = data['category']

    # pp(data)
    file_name = f'stick_figure_{category}.png'
    file_name = file_name.lower()
    file_path_stick_figure =  os.path.join(fps.page_statistics2_equivalent_objects_directory, file_name)

    directory_path = os.path.join(fps.page_statistics2_equivalent_objects_directory, f'Equivalent{category.title()}')

    pictures = get_sorted_pictures(directory_path, data['units'][0].upper() )
    # pp(pictures)
    target_idx = get_closest_index(pictures, cumulative_value)
    picture_data = pictures[target_idx]
    picture_filename = picture_data['filename']

    picture_filepath = os.path.join(directory_path, picture_filename)
    picture_extension = os.path.splitext(picture_filepath)[1][1:]
    picture_description = picture_data['description']
    comparison_value = picture_data['value']

    times = round((cumulative_value / comparison_value) * 100)
    equivalence_formatted = f'{times:,} %'
    # TODO: make this a method that only allows mininum decimal places if less than 10
    # if times < 0.1:
    #     equivalence_formatted = f'{times:.2f}'
    # elif times < 10:
    #     equivalence_formatted = f'{times:.1f}'
    # else:
    #     equivalence_formatted = f'{times:,.0f}'


    markdown_text_equivalence = f'### {equivalence_formatted}\n##### {picture_description}'


    return (markdown_text,
            b64_image(file_path_stick_figure, 'png'),
            b64_image(picture_filepath, picture_extension),
            markdown_text_equivalence)



