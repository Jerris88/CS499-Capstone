from dash import Input, Output, State, no_update


# registers login and logout callbacks
def register_auth_callbacks(app, admin_auth):

    # handle admin login
    @app.callback(
        Output("login-state", "data", allow_duplicate=True),
        Output("login-output", "children"),
        Output("url", "pathname", allow_duplicate=True),
        Input("login-button", "n_clicks"),
        State("login-username", "value"),
        State("login-password", "value"),
        prevent_initial_call=True,
    )
    def handle_login(n_clicks, username, password):
        if not n_clicks:
            return no_update, no_update, no_update

        # both fields are needed before checking the database
        if not username or not password:
            return no_update, "Please enter both username and password.", no_update

        is_valid_admin = admin_auth.verify_admin_user(username, password)

        # successful login stores session data and sends user to admin page
        if is_valid_admin:
            return {"logged_in": True, "username": username}, "Login successful.", "/admin"

        # failed login keeps user on login page
        return {
            "logged_in": False,
            "username": None,
        }, "Invalid username or password.", no_update

    # handle admin logout
    @app.callback(
        Output("login-state", "data", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Input("logout-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_logout(n_clicks):
        if not n_clicks:
            return no_update, no_update

        # clear session state and send user back to home page
        return {"logged_in": False, "username": None}, "/"