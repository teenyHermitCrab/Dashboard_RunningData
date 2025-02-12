import dash
from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
import assets.file_paths as fps
from pages.overview import sidebar

pd.options.mode.chained_assignment = None  # default='warn'



def placeholder():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([ dcc.Markdown(['### under dev']), ]),
                ])
            ])
        )
    ])



def layout():
    layout_statistics = [
        sidebar(__name__),
        html.Div([
            dbc.Container(placeholder(), fluid=True),
        ], className='content')
    ]

    return layout_statistics