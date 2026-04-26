from dash import html, dcc


# builds the admin login page
def create_login_layout():
    return html.Div([

        # page header
        html.Div([
            html.H1("Admin Login", className="admin-title"),
            html.P(
                "Sign in to access administrative tools.",
                className="admin-subtitle"
            )
        ], className="admin-header"),

        # login form container
        html.Div([

            html.H3("Login Credentials"),

            html.Div([

                # username input
                html.Label("Username", className="admin-label"),
                dcc.Input(
                    id="login-username",
                    type="text",
                    placeholder="Enter username",
                    className="admin-input"
                ),

                # password input
                html.Label("Password", className="admin-label"),
                dcc.Input(
                    id="login-password",
                    type="password",
                    placeholder="Enter password",
                    className="admin-input"
                ),

                # login button triggers auth callback
                html.Button(
                    "Login",
                    id="login-button",
                    n_clicks=0,
                    className="admin-btn update",
                    style={"marginTop": "15px"}
                ),

                # displays login success/failure message
                html.Div(
                    id="login-output",
                    className="admin-message"
                )

            ], className="admin-form-group")

        ], className="admin-card password-card")

    ], className="admin-page")