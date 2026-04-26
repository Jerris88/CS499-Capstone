from dash import html, dcc


def create_admin_layout():
    return html.Div([

        html.H1("Admin Page"),

        html.H3("Manage Animal Records"),

        html.Div([

            html.Label("Animal ID"),
            dcc.Input(id="input-animal-id", type="text"),

            html.Br(),

            html.Label("Animal Type"),
            dcc.Input(id="input-animal-type", type="text"),

            html.Br(),

            html.Label("Breed"),
            dcc.Input(id="input-breed", type="text"),

            html.Br(),

            html.Label("Outcome Type"),
            dcc.Input(id="input-outcome", type="text"),

            html.Br(),
            html.Br(),

            html.Button("Create Record", id="btn-create", n_clicks=0),
            html.Button("Update Selected", id="btn-update", n_clicks=0),
            html.Button("Delete Selected", id="btn-delete", n_clicks=0),

            html.Br(),
            html.Br(),

            html.Div(id="admin-output")
        ])
    ])