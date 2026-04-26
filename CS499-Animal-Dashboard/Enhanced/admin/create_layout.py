from dash import html, dcc


# builds the admin create record page
def create_admin_create_layout():
    return html.Div([

        # ======================
        # HEADER
        # ======================
        html.Div([
            html.Div([
                html.H1("Create Record", className="admin-title"),
                html.P(
                    "Enter the required intake information for a new animal record.",
                    className="admin-subtitle",
                ),
            ], className="admin-header-text"),
        ], className="admin-header"),

        # ======================
        # CREATE RECORD FORM
        # ======================
        html.Div([

            html.H3([
                html.Img(
                    src="/assets/paw.svg",
                    style={
                        "width": "22px",
                        "marginRight": "10px",
                        "verticalAlign": "middle",
                    },
                ),
                "New Animal Intake Form",
            ]),

            html.Div([

                # basic animal info
                html.Div([
                    html.Label("Animal ID", className="admin-label"),
                    dcc.Input(
                        id="create-animal-id",
                        type="text",
                        placeholder="Enter animal ID",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                html.Div([
                    html.Label("Name", className="admin-label"),
                    dcc.Input(
                        id="create-name",
                        type="text",
                        placeholder="Enter animal name",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                html.Div([
                    html.Label("Animal Type", className="admin-label"),
                    dcc.Input(
                        id="create-animal-type",
                        type="text",
                        placeholder="Enter animal type",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                html.Div([
                    html.Label("Breed", className="admin-label"),
                    dcc.Input(
                        id="create-breed",
                        type="text",
                        placeholder="Enter breed",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                html.Div([
                    html.Label("Color", className="admin-label"),
                    dcc.Input(
                        id="create-color",
                        type="text",
                        placeholder="Enter color",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                # outcome-related fields
                html.Div([
                    html.Label("Sex Upon Outcome", className="admin-label"),
                    dcc.Input(
                        id="create-sex-upon-outcome",
                        type="text",
                        placeholder="Enter sex upon outcome",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                html.Div([
                    html.Label("Age Upon Outcome (Weeks)", className="admin-label"),
                    dcc.Input(
                        id="create-age-upon-outcome-in-weeks",
                        type="number",
                        placeholder="Enter age in weeks",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                html.Div([
                    html.Label("Outcome Type", className="admin-label"),
                    dcc.Input(
                        id="create-outcome-type",
                        type="text",
                        placeholder="Enter outcome type",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                # location info for map
                html.Div([
                    html.Label("Location Latitude", className="admin-label"),
                    dcc.Input(
                        id="create-location-lat",
                        type="number",
                        placeholder="Enter latitude",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                html.Div([
                    html.Label("Location Longitude", className="admin-label"),
                    dcc.Input(
                        id="create-location-long",
                        type="number",
                        placeholder="Enter longitude",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                # create button and output message
                html.Div([
                    html.Button(
                        "Create Record",
                        id="btn-create",
                        n_clicks=0,
                        className="admin-btn create",
                    ),

                    html.Div(
                        id="create-output",
                        className="admin-message",
                    ),

                ], className="admin-form-group full-width"),

            ], className="admin-form-grid"),

        ], className="admin-card records-card"),

    ], className="admin-page")