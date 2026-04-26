from dash import html, dcc


# builds the admin security page (password management)
def create_admin_security_layout():
    return html.Div([

        # ======================
        # HEADER
        # ======================
        html.Div([
            html.Div([
                html.H1("Security Settings", className="admin-title"),
                html.P(
                    "Update your password and manage account security settings.",
                    className="admin-subtitle",
                ),
            ], className="admin-header-text"),
        ], className="admin-header"),

        # ======================
        # CHANGE PASSWORD SECTION
        # ======================
        html.Div([

            html.H3([
                html.Img(
                    src="/assets/paw.svg",
                    style={
                        "width": "22px",
                        "marginRight": "10px",
                        "verticalAlign": "middle",
                        "filter": "hue-rotate(260deg)",
                    },
                ),
                "Change Password",
            ]),

            html.Div([

                # current password input
                html.Div([
                    html.Label("Current Password", className="admin-label"),
                    dcc.Input(
                        id="current-password",
                        type="password",
                        placeholder="Enter current password",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                # new password input
                html.Div([
                    html.Label("New Password", className="admin-label"),
                    dcc.Input(
                        id="new-password",
                        type="password",
                        placeholder="Enter new password",
                        className="admin-input",
                    ),
                ], className="admin-form-group"),

                # submit button and messages
                html.Div([
                    html.Button(
                        "Change Password",
                        id="btn-change-password",
                        n_clicks=0,
                        className="admin-btn password",
                    ),

                    html.Div(
                        id="password-output",
                        className="admin-message",
                    ),

                    html.Div(
                        "Use a strong password and keep it private.",
                        className="password-note",
                    ),

                ], className="admin-form-group full-width"),

            ], className="admin-form-grid"),

        ], className="admin-card password-card"),

    ], className="admin-page")