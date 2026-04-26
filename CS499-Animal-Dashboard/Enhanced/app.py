import pandas as pd
from dash import Dash, html, dcc, Input, Output, State

from config.app_config import AppConfig
from database.shelter import AnimalShelter
from database.admin_auth import AdminAuth
from dashboard.layout import create_layout
from dashboard.callbacks import register_callbacks
from admin.create_layout import create_admin_create_layout
from admin.edit_layout import create_admin_edit_layout
from admin.security_layout import create_admin_security_layout
from admin.callbacks import register_admin_callbacks
from auth.layout import create_login_layout
from auth.callbacks import register_auth_callbacks
from analytics.layout import create_analytics_layout
from analytics.callbacks import register_analytics_callbacks


# ---------------------------
# Initialize App
# ---------------------------
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = AppConfig.APP_TITLE


# ---------------------------
# Load Data Function
# ---------------------------
def load_data(shelter):
    records = shelter.read({})
    df = pd.DataFrame.from_records(records)

    if "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)

    return df


# ---------------------------
# Create Database Instances
# ---------------------------
shelter = AnimalShelter(
    user=AppConfig.USERNAME,
    pwd=AppConfig.PASSWORD,
    host=AppConfig.HOST,
    port=AppConfig.PORT,
    db=AppConfig.DB_NAME,
    collection=AppConfig.ANIMAL_COLLECTION,
)

admin_auth = AdminAuth(
    user=AppConfig.USERNAME,
    pwd=AppConfig.PASSWORD,
    host=AppConfig.HOST,
    port=AppConfig.PORT,
    db=AppConfig.DB_NAME,
    collection=AppConfig.ADMIN_COLLECTION
)


# ---------------------------
# Load Initial Data
# ---------------------------
df = load_data(shelter)


# ---------------------------
# App Layout
# ---------------------------
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(
        id="login-state",
        data={"logged_in": False, "username": None},
        storage_type="session"
    ),

    html.Div(id="nav-links"),

    html.Hr(),

    html.Div(id="page-content")
])


# ---------------------------
# Navigation
# ---------------------------
@app.callback(
    Output("nav-links", "children"),
    Input("login-state", "data"),
    Input("url", "pathname")
)
def update_nav(login_state, pathname):
    logged_in = login_state.get("logged_in", False) if login_state else False
    username = login_state.get("username") if login_state else None

    nav_items = [
        dcc.Link("Dashboard", href="/", style={"marginRight": "20px"}),
        dcc.Link("Analytics", href="/analytics", style={"marginRight": "20px"})
    ]

    if logged_in:
        nav_items.extend([
            dcc.Link("Create Record", href="/admin/create", style={"marginRight": "20px"}),
            dcc.Link("Edit/Delete Record", href="/admin/edit", style={"marginRight": "20px"}),
            dcc.Link("Security", href="/admin/security", style={"marginRight": "20px"}),
            html.Span(
                f"Logged in as {username}",
                style={"marginRight": "20px"}
            ),
            html.Button("Logout", id="logout-button", n_clicks=0)
        ])
    else:
        nav_items.append(
            dcc.Link("Admin Login", href="/login")
        )

    return html.Div(nav_items, style={"padding": "10px 20px"})


# ---------------------------
# Page Routing
# ---------------------------
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    State("login-state", "data")
)
def display_page(pathname, login_state):
    logged_in = login_state.get("logged_in", False) if login_state else False

    if pathname == "/login":
        return create_login_layout()

    if pathname == "/admin/create":
        if logged_in:
            return create_admin_create_layout()
        return create_login_layout()

    if pathname == "/admin/edit":
        if logged_in:
            return create_admin_edit_layout(df)
        return create_login_layout()

    if pathname == "/admin/security":
        if logged_in:
            return create_admin_security_layout()
        return create_login_layout()

    if pathname == "/analytics":
        return create_analytics_layout()

    return create_layout(df)


# ---------------------------
# Register Callbacks
# ---------------------------
register_callbacks(app, shelter)
register_admin_callbacks(app, shelter, admin_auth)
register_auth_callbacks(app, admin_auth)
register_analytics_callbacks(app, shelter)


# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)