from dash import callback, html, Input, Output, State
import dash_bootstrap_components as dbc


@callback(Output('sidebar', 'className'),  #className
    Input('sidebarCollapse', 'n_clicks'),
    State('sidebar', 'className'))
def toggle_sidebar(btn_click, className):
    """
    Callback for expanding, contracting sidebar (initially hidden on small screens)

    Args:
        btn_click (int): Number of times button has been clicked, value not used
        className (str): current css style of sidebar

    Returns:
        className for sidebar.  This toggles sidebar visibility
    """
    if className == 'active':
        return ''
    if className == '':
        return 'active'


def sidebar(active_item=None):
    """
    Returns layout for sidebar

    Args:
        active_item (str | None): Used for highlight of NavLinks

    Returns:
        html.Nav object that comprises sidebar
    """
    nav = html.Nav(id="sidebar", className="active", children=[
                    html.Div(className="custom-menu", children=[
                        html.Button([
                            html.I(className="fa fa-bars"),  # font-awesome icon: the burger menu icon
                            html.Span("Toggle Menu", className="sr-only")
                        ], type="button",
                           id="sidebarCollapse",
                           className="btn btn-primary")
                    ]),
                    html.Div(className="flex-column p-4 nav nav-pills", children=[
                        html.A([
                            html.I(className="fa-solid fa-earth-americas fa-4x mx-2",),
                            html.Span(" Run Data", className='fs-4'),

                        ], className='d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none', href='/'),
                        html.Br(),
                        html.P('Data visualization experiments using personal Strava data', ),
                        html.Hr(),
                        dbc.NavItem(dbc.NavLink("Overview",          href="/",             className='text-white', active=True if active_item == 'Pages.overview'     else False)),
                        dbc.NavItem(dbc.NavLink("Statistics",        href="/statistics_1", className='text-white', active=True if active_item == 'Pages.statistics_1' else False)),
                        dbc.NavItem(dbc.NavLink("Fun Statistics 😀", href="/statistics_2", className='text-white', active=True if active_item == 'Pages.statistics_2' else False)),
                        dbc.NavItem(dbc.NavLink("Lake Sonoma",       href="/lake_sonoma",  className='text-white', active=True if active_item == 'Pages.lake_sonoma'  else False)),
                        dbc.NavItem(dbc.NavLink("About",             href="/about",        className='text-white', active=True if active_item == 'Pages.about'        else False)),
                    ])
    ])
    return nav