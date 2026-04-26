from dash import html, dcc, dash_table
import dash_leaflet as dl

from breed_utils import get_top_breed_options


# builds the main dashboard page
def create_layout(df):
    return html.Div([

        # ======================
        # Header
        # ======================
        html.Div([
            html.H1("Grazioso Salvare Dashboard", className="dashboard-title"),

            html.Img(
                src="/assets/GraziosoSalvareLogo.png",
                className="dashboard-logo",
            ),

            html.P(
                "Review rescue categories, breed trends, and mapped animal locations.",
                className="dashboard-subtitle",
            ),
        ], className="dashboard-header"),

        # ======================
        # Filters
        # ======================
        html.Div([

            # rescue category radio buttons
            html.Div([
                html.H3("Rescue Filter"),

                dcc.RadioItems(
                    id="filter-type",
                    options=[
                        {"label": "All", "value": "all"},
                        {"label": "Water Rescue", "value": "water"},
                        {"label": "Mountain/Wilderness Rescue", "value": "mountain"},
                        {"label": "Disaster Rescue", "value": "disaster"},
                    ],
                    value="all",
                    inline=True,
                    className="dashboard-radio-group",
                ),
            ], className="dashboard-filter-column"),

            # breed dropdown uses the most common breeds from the dataset
            html.Div([
                html.H3("Breed Search"),

                dcc.Dropdown(
                    id="breed-group-filter",
                    options=get_top_breed_options(df, top_n=15),
                    value="all",
                    clearable=False,
                    className="dashboard-dropdown",
                ),
            ], className="dashboard-filter-column"),

        ], className="dashboard-card dashboard-filter-card"),

        # shows which filters are currently applied
        html.Div(
            id="active-filters",
            className="dashboard-subtitle",
        ),

        # ======================
        # Table and Chart
        # ======================
        html.Div([

            # main animal record table
            html.Div([
                html.H3("Animal Records"),

                html.Div([
                    dash_table.DataTable(
                        id="datatable-id",
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict("records"),
                        page_size=10,
                        row_selectable="single",
                        selected_rows=[0],
                        sort_action="native",
                        filter_action="native",
                        style_table={"overflowX": "auto", "height": "420px"},
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
                    )
                ], className="dashboard-table-wrap"),
            ], className="dashboard-card dashboard-table-card"),

            # breed chart updates with the selected filters
            html.Div([
                html.H3("Breed Distribution"),

                dcc.Graph(
                    id="pie-chart",
                    style={"height": "420px"},
                ),
            ], className="dashboard-card dashboard-chart-card"),

        ], className="dashboard-two-col"),

        # ======================
        # Map
        # ======================
        html.Div([
            html.H3("Selected Animal Location"),

            dl.Map(
                id="map-id",
                center=[30.75, -97.48],
                zoom=10,
                children=[dl.TileLayer()],
                className="dashboard-map",
            ),
        ], className="dashboard-card dashboard-map-card"),

    ], className="dashboard-page")