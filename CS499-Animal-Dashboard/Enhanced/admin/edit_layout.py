from dash import html, dcc, dash_table
import pandas as pd


# builds the admin edit/delete page
def create_admin_edit_layout(df=None):
    if df is None:
        df = pd.DataFrame()

    return html.Div([

        # ======================
        # HEADER
        # ======================
        html.Div([
            html.Div([
                html.H1("Edit / Delete Record", className="admin-title"),
                html.P(
                    "Select a row, edit values directly in the table, then update or delete the selected record.",
                    className="admin-subtitle",
                ),
                html.P(
                    "Note: Animal ID cannot be edited.",
                    className="admin-subtitle",
                ),
            ], className="admin-header-text"),
        ], className="admin-header"),

        # keeps track of the selected animal id
        dcc.Store(id="selected-animal-id"),

        # ======================
        # ACTION BUTTONS
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
                "Record Actions",
            ]),

            html.Div([
                html.Button(
                    "Update Selected",
                    id="btn-update",
                    n_clicks=0,
                    className="admin-btn update",
                    disabled=True,
                ),

                html.Button(
                    "Delete Selected",
                    id="btn-delete",
                    n_clicks=0,
                    className="admin-btn delete",
                    disabled=True,
                ),

                dcc.ConfirmDialog(
                    id="confirm-delete-dialog",
                    message="Are you sure you want to delete this selected record?",
                ),
            ], className="admin-button-row"),

            html.Div(
                id="edit-output",
                className="admin-message",
            ),

        ], className="admin-card records-card"),

        # ======================
        # EDITABLE TABLE
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
                "Editable Admin Records Table",
            ]),

            dash_table.DataTable(
                id="admin-datatable-id",
                columns=[
                    {
                        "name": i,
                        "id": i,
                        "editable": False if i == "animal_id" else True,
                    }
                    for i in df.columns
                ],
                data=df.to_dict("records"),
                page_size=10,
                row_selectable="single",
                selected_rows=[],
                editable=True,
                sort_action="native",
                filter_action="native",
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "padding": "10px",
                    "minWidth": "120px",
                    "maxWidth": "220px",
                    "whiteSpace": "normal",
                },
                style_header={
                    "fontWeight": "bold",
                },
            ),

        ], className="admin-card records-card"),

    ], className="admin-page")