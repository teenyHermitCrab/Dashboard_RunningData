from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import base64
import Assets.file_paths as fps
from Pages.sidebar import sidebar

with open(fps.page_about_markdown_path, 'r') as f:
    markdown_text = f.read()

banner_path = fps.page_about_banner_path
resume_path = fps.page_about_resume_path
profile_pic_number = 0  # TODO: replace this with dcc.Store if you are allergic to globals.  We alter this inside button callback



def layout():
    # TODO: i thought png files didnt need encoding..?  Check this out
    encoded_image = base64.b64encode(open(banner_path, 'rb').read())

    banner = dbc.Row([
        dbc.Col([
            html.Div([
                # see style.css file for this className
                html.Img(
                    src='data:image/png;base64,{}'.format(encoded_image.decode()),
                    className='banner-image'
                ),
                html.Div([
                    dbc.Button("about author", id="btn_open_modal_about_author", n_clicks=0),
                ], className='overlay-text')  # className='overlay-text'
            ], className='banner-container')
        ]),
    ])

    layout_about = [
        sidebar(__name__),
        html.Div([
            # Banner container: a full-width (fluid) container for the banner
            dbc.Container(banner, fluid=True),

            # Markdown container
            dbc.Container([
                dbc.Row(
                    # Column with Bootstrap spacing classes:
                    # - 'mt-4': adds a top margin (spacing level 4)
                    # - 'ms-4': adds a left margin (using "start" for RTL compatibility)
                    dbc.Col([
                        dcc.Markdown(markdown_text, style={"textAlign": "justify"}),
                    ], className='mt-4 ms-4')
                ),
            ], fluid=True),

            # modal is toggled when 'about-author' button pressed
            dbc.Modal([
                dbc.ModalHeader(
                    dbc.ModalTitle('Chris Reyes')
                ),
                dbc.ModalBody([
                    get_modal_body()
                ]),
                dbc.ModalFooter([
                    html.Li([
                        html.Br(),
                        # GitHub icon link using Font Awesome and Bootstrap margin:
                        # - 'fa-brands' and 'fa-github': specify the GitHub brand icon from Font Awesome
                        # - 'me-3': adds a right margin (spacing level 3) for spacing between icons
                        # - 'fa-1x': sets the icon size to the standard 1x scale
                        html.A(
                            [html.I(className="fa-brands fa-github me-3 fa-1x")],
                            href='https://github.com/teenyHermitCrab',
                            target='_blank'
                        ),
                        # LinkedIn icon link with similar classes:
                        # - 'fa-brands' and 'fa-linkedin': specify the LinkedIn brand icon
                        # - 'me-3' and 'fa-1x' serve the same spacing and size purposes as above
                        html.A(
                            [html.I(className="fa-brands fa-linkedin me-3 fa-1x")],
                            href='https://www.linkedin.com/in/christopher-reyes-mfg-test/',
                            target='_blank'
                        ),
                        # - 'ml-10': adds a left margin (spacing level 10)
                        # - 'mr-10': adds a right margin (spacing level 10)
                        html.A(
                            [dbc.Button('resume')],
                            href=resume_path,
                            title='Chris Reyes resume',
                            target='_blank',
                            className='ml-10 mr-10'
                        ),
                    ],
                    # List items with multiple Bootstrap utility classes:
                    # - 'list-unstyled': removes default bullet styling from the list
                    # - 'float-end': floats the element to the right (end of the container)
                    # - 'navbar': applies navbar styling (often used for consistent nav item appearance)
                    className='list-unstyled float-end navbar'
                    )
                ]),
            ], id="modal_about_author", is_open=False),
        ], className='content')  # find 'content' style in style.css
    ]

    return layout_about






# TODO: move this to file in assets file.  Individual fields would be fields in that file
def get_modal_body():
    profile_base_path = fps.footnote_profile_pic_base_path
    # Replace the placeholder 'X' with 0 to form the actual profile picture path. profile_0 is the initial photo
    profile_path = profile_base_path.replace('X', str(0))

    modal_body = html.Div([
        html.Div([html.Img(id='image_profile_picture',
                           src=profile_path,
                           width=250,
                           # Bootstrap classes applied:
                           # - 'rounded-circle': makes the image circular.
                           # - 'mx-auto': centers the image horizontally within its container.
                           # - 'd-flex': sets the display property to flex, useful for alignment.
                           # - 'img-thumbnail': adds a border, padding, and a background to mimic a thumbnail.
                           className="rounded-circle mx-auto d-flex img-thumbnail")
                  ]),
        html.Br(),
        html.P(" Coffee Drinker  |  Trail Runner  |  Mote of Dust ", className='text-center'),  # Bootstrap classes applied: 'text-center': centered text
        html.Br(),
        html.P(" Chris Reyes holds a bachelor's degree in Computer Engineering from UC Santa Cruz. He has 15+ years experience in manufacture test software development, mostly working in Python and C#. He has been a key contributor on teams in telecommunications, renewable energy, and medical industries.",
               # Bootstrap classes applied: 'text-justify': justified text
               className='text-justify'),
        html.Br(),
        html.P("His main areas of interest are weird rocks, pareidolia (e.g., 'that cloud looks like a dragon!' ), and overthinking normal household projects.",
               className='text-justify'),
    ])
    return modal_body


@callback(Output("modal_about_author", "is_open"),
          Output('image_profile_picture', 'src'),
          Input("btn_open_modal_about_author", "n_clicks"),
          State("modal_about_author", "is_open"))
def toggle_about_author_modal(n1, is_open):
    # TODO: use a dcc.Store() rather than global variable?
    # If it was dcc.Store, then it would be stored on local machine. For an int this is not a lot of data.
    # But it really doesn't need to be on local machine if the callback is on the server..  Correct..?
    #
    # we want a variable outside this method so that we can cycle through profile pictures at each opening of modal
    global profile_pic_number
    profile_base_path = fps.footnote_profile_pic_base_path
    profile_path = profile_base_path.replace('X', str(profile_pic_number))
    src = profile_path

    if n1:
        if not is_open:
            # for this to work, we have 10 profile pictures, numbered 0-9
            profile_pic_number = n1 % 10
            profile_base_path = fps.footnote_profile_pic_base_path
            profile_path = profile_base_path.replace('X', str(profile_pic_number))
            src = profile_path
        return not is_open, src
    return is_open, src
