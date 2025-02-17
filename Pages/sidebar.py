from dash import html
import dash_bootstrap_components as dbc

def sidebar(active_item=None):
    nav = html.Nav(id="sidebar", className="active", children=[
                    html.Div(className="custom-menu", children=[
                        html.Button([
                            html.I(className="fa fa-bars"),
                            html.Span("Toggle Menu", className="sr-only")
                        ], type="button",
                           id="sidebarCollapse",
                           className="btn btn-primary")
                    ]),
                    html.Div(className="flex-column p-4 nav nav-pills", children=[
                        html.A([
                            html.I(className="fa-solid fa-earth-americas fa-4x mx-2",),
                            #html.Img(src='https://webstatic.everburstsun.net/dash-molstar-example/nav.png', alt='', width=48, height=48, className='mx-2'),
                            html.Span(" Run Data", className='fs-4'),
                        ], className='d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none', href='/'),
                        html.Br(),
                        html.P('Data visualization experiments using personal Strava data', ),
                        html.Hr(),
                        dbc.NavItem(dbc.NavLink("Overview", href="/", className='text-white', active=True if active_item=='Pages.overview' else False)),
                        dbc.NavItem(dbc.NavLink("Statistics", href="/statistics_1", className='text-white', active=True if active_item=='Pages.statistics_1' else False)),
                        # dbc.NavItem(dbc.NavLink("Statistics 2", href="/statistics_2", className='text-white', active=True if active_item == 'Pages.statistics_2' else False)),
                        dbc.NavItem(dbc.NavLink("Lake Sonoma", href="/lake_sonoma", className='text-white', active=True if active_item=='Pages.lake_sonoma' else False)),
                        dbc.NavItem(dbc.NavLink("About", href="/about", className='text-white', active=True if active_item=='Pages.about' else False))
                    ])
    ])
    return nav