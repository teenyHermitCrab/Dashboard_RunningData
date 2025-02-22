import dash
from dash import Dash
import dash_bootstrap_components as dbc
# from flask import Flask
from Pages import overview, statistics_1, lake_sonoma, about

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.2.4/dbc.min.css"
# app = Flask(__name__, instance_relative_config=True)
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
    name='Overview',
    layout=overview.layout)
dash.register_page('Pages.statistics_1',
    path='/statistics_1',
    title='Statistics 1',
    name='Statistics 1',
    layout=statistics_1.layout)
# dash.register_page('Pages.statistics_2',
#     path='/statistics_2',
#     title='Statistics 2',
#     name='Statistics 2',
#     layout=statistics_2.layout)
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
app.layout = dash.page_container



if __name__ == "__main__":
    app.run_server(debug=True)