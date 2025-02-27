from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import base64
import Assets.file_paths as fps
from Pages.sidebar import sidebar

with open(fps.page_about_markdown_path, 'r') as f:
    markdown_text = f.read()

banner_path = fps.page_about_banner_path
resume_path = fps.page_about_resume_path



def layout():
    # TODO: i thought png files didnt need encoding..?  Check this out
    encoded_image = base64.b64encode(open(banner_path, 'rb').read())

    banner = dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), className='banner-image'),

                html.Div([
                    dbc.Button("about author", id="btn_open_modal_about_author", n_clicks=0, ),
                ],
                   className='overlay-text')  # className='overlay-text'
            ], className='banner-container')
        ]),
    ])

    layout_about = [
        sidebar(__name__),
        html.Div([
            dbc.Container(banner, fluid=True),
            dbc.Container([
                dbc.Row(
                    dbc.Col(
                        dcc.Markdown(markdown_text, style={"textAlign": "justify"}), className='mt-4 ms-4')
                ),
            ], fluid=True),

            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle('Chris Reyes')),
                dbc.ModalBody([get_modal_body()]),
                dbc.ModalFooter([
                    html.Li([
                        html.Br(),

                        html.A([html.I(className="fa-brands fa-github me-3 fa-1x")],
                               href='https://github.com/teenyHermitCrab',
                               target='_blank'
                               ),
                        html.A([html.I(className="fa-brands fa-linkedin me-3 fa-1x")],
                               href='https://www.linkedin.com/in/christopher-reyes-mfg-test/',
                               target='_blank'
                               ),
                        html.A([dbc.Button('resume', )], href=resume_path, title='Chris Reyes resume', target='_blank', className='ml-10 mr-10'),

                    ], className='list-unstyled float-end navbar')
                    # dont include list marks, let element float to available right)
                ], )
            ], id="modal_about_author",
                is_open=False,
            ),

        ], className='content')
    ]

    return layout_about



profile_pic_number = 0  # TODO: replace this with dcc.Store

# TODO: move this to file in assets file.  Individual fields would be fields in that file
def get_modal_body():
    profile_base_path = fps.footnote_profile_pic_base_path
    profile_path = profile_base_path.replace('X', str(0))

    modal_body = html.Div([
        html.Div([html.Img(id='image_profile_picture',
                           src=profile_path,
                           width=250,
                           className="rounded-circle mx-auto d-flex img-thumbnail")
                  ]),
        html.Br(),
        html.P(" Coffee Drinker  |  Trail Runner  |  Mote of Dust ", className='text-center'),
        html.Br(),
        html.P(" Chris Reyes holds a bachelor's degree in Computer Engineering from UC Santa Cruz. He has 15+ years experience in manufacture test software development, mostly working in Python and C#. He has been a key contributor on teams in telecommunications, renewable energy, and medical industries.",
               className='text-justify'),
        html.Br(),
        html.P("His main areas of interest are weird rocks, pareidolia (e.g., 'that cloud looks like a dragon!' ), and overthinking normal household projects.",
               className='justify-center'),
    ])
    return modal_body


@callback(Output("modal_about_author", "is_open"),
          Output('image_profile_picture', 'src'),
          Input("btn_open_modal_about_author", "n_clicks"),
          State("modal_about_author", "is_open"))
def toggle_about_author_modal(n1, is_open):
    # TODO: use a dcc.Store() rather than global variable
    global profile_pic_number
    profile_base_path = fps.footnote_profile_pic_base_path
    profile_path = profile_base_path.replace('X', str(profile_pic_number))
    src = profile_path

    if n1:
        if not is_open:
            profile_pic_number = n1 % 10
            profile_base_path = fps.footnote_profile_pic_base_path
            profile_path = profile_base_path.replace('X', str(profile_pic_number))
            src = profile_path
        return not is_open, src
    return is_open, src




