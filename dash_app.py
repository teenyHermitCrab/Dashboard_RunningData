import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
# import json
# import pandas as pd
# from pprint import pprint as pp
# from Assets import file_paths as fps
from Pages import overview, statistics_1, statistics_2, lake_sonoma, about

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.2.4/dbc.min.css"
app = Dash(__name__,
        # server=app,
        use_pages=True,
        assets_folder='Assets',
        external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME, dbc_css],
    )
server = app.server


dash.register_page('Pages.homepage',
    path='/',
    title='Overview',
    name='Corks Run on Planet 3!',
    description='Experiments in data visualization using personal Strava data.',
    layout=overview.layout)
dash.register_page('Pages.statistics_1',
    path='/statistics_1',
    title='Statistics 1',
    name='Statistics 1',
    layout=statistics_1.layout)
dash.register_page('Pages.statistics_2',
    path='/statistics_2',
    title='Statistics 2',
    name='Statistics 2',
    layout=statistics_2.layout)
dash.register_page('Pages.lake_sonoma',
    path='/lake_sonoma',
    title='Lake Sonoma',
    name='Lake Sonoma',
    layout=lake_sonoma.layout)
dash.register_page('Pages.about',
    path='/about',
    title='About',
    name='About',
    layout=about.layout)


# with app.app_context():
#     dash_app.layout = dash.page_container

# Need to investigate: will dcc.Store have any value without clientside callbacks?

app.layout = html.Div( [
                        # dcc.Store(id='storage_df_all_runs', data=df_all_runs.to_dict('records')),
                        # dcc.Store(id='storage_json_counties', data = json_counties),
                        # dcc.Store(id='storage_dict_fips_to_name', data=fips_to_name),
                        # dcc.Store(id='storage_df_lake_sonoma_all_runs', data=df_all_LS_runs.to_dict('records')),
                        # dcc.Store(id='storage_df_topo_lake_sonoma', data=df_topo.to_dict('records')),
                        # dcc.Store(id='storage_df_lake_sonoma_100K_run', data=df_100K_run.to_dict('records')),
                        # dcc.Store(id='storage_nparray_lake_sonoma_Z', data=Z.tolist()),
                        # dcc.Store(id='storage_nparray_lake_sonoma_Z_water', data=Z_water.tolist()),
                        dash.page_container ])


# Add meta tags to the head of the app
app.index_string = r'''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>My Dash App</title>
        <meta property="og:title" content="Corks on trails!" />
        <meta property="og:description" content="Explorations of Strava data." />
        <meta property="og:image" content="C:\Users\CorkHorde\Documents\Projects\StravaRunningData\Assets\skaggs_overlook_sm.jpg" />
        <meta property="og:url" content="https://www.corkhorde.com" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


if __name__ == "__main__":
    app.run_server(debug=True)
