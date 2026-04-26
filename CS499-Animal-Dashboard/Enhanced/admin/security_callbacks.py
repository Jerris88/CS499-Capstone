from dash import Input, Output, State, no_update


# registers password change callback
def register_security_callbacks(app, admin_auth):

    # ======================
    # CHANGE PASSWORD
    # ======================
    @app.callback(
        Output("password-output", "children"),
        Output("password-output", "className"),
        Input("btn-change-password", "n_clicks"),
        State("current-password", "value"),
        State("new-password", "value"),
        State("login-state", "data"),
        prevent_initial_call=True,
    )
    def change_password(n_clicks, current_password, new_password, login_state):
        if not n_clicks:
            return no_update

        # user has to be logged in before changing password
        if not login_state or not login_state.get("logged_in"):
            return "You must be logged in to change your password.", "admin-message error"

        username = login_state.get("username")

        if not username:
            return "No logged-in user was found.", "admin-message error"

        # both fields are needed for the password update
        if not current_password or not new_password:
            return "Please enter both your current and new password.", "admin-message error"

        # make sure the current password is correct first
        is_valid_user = admin_auth.verify_admin_user(username, current_password)

        if not is_valid_user:
            return "Current password is incorrect.", "admin-message error"

        password_updated = admin_auth.update_admin_password(username, new_password)

        if password_updated:
            return "Password changed successfully.", "admin-message success"

        return "Password update failed.", "admin-message error"