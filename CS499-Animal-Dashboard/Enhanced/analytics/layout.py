from dash import html, dcc


# builds the analytics page layout
def create_analytics_layout():
    return html.Div([

        html.Div([

            # left column holds title and scorecards
            html.Div([

                html.Div([
                    html.H1("Analytics Dashboard", className="dashboard-title"),

                    html.Img(
                        src="/assets/GraziosoSalvareLogo.png",
                        className="analytics-logo",
                    ),

                    html.P(
                        "Review shelter outcome performance by animal type and breed.",
                        className="dashboard-subtitle",
                    ),
                ], className="analytics-title-panel"),

                html.Div([
                    html.H3("Outcome Summary Metrics"),

                    html.Div(
                        id="analytics-scorecards",
                        className="scorecard-grid",
                    ),

                ], className="dashboard-card analytics-scorecard-card"),

            ], className="analytics-left-column"),

            # right column holds filters and charts
            html.Div([

                html.Div([
                    html.H3("Analytics Filters"),

                    html.Div([

                        # animal type filter
                        html.Div([
                            html.Label("Animal Type", className="filter-label"),

                            dcc.RadioItems(
                                id="analytics-animal-type",
                                options=[
                                    {"label": "All Animals", "value": "All"},
                                    {"label": "Dogs", "value": "Dog"},
                                    {"label": "Cats", "value": "Cat"},
                                    {"label": "Other", "value": "Other"},
                                ],
                                value="All",
                                inline=True,
                                className="analytics-radio-group",
                            ),
                        ], className="analytics-filter-item"),

                        # breed filter gets filled by callback
                        html.Div([
                            html.Label("Breed", className="filter-label"),

                            dcc.Dropdown(
                                id="analytics-breed-filter",
                                options=[],
                                value="All",
                                clearable=False,
                                placeholder="Select a breed",
                                className="analytics-breed-dropdown",
                            ),
                        ], className="analytics-filter-item"),

                    ], className="analytics-filter-row"),

                ], className="dashboard-card analytics-filter-card"),

                # side-by-side analytics charts
                html.Div([

                    html.Div([
                        html.H3("Age Category Distribution"),

                        html.P(
                            "Age breakdown of selected animals.",
                            className="dashboard-subtitle",
                            style={"textAlign": "center", "marginBottom": "10px"},
                        ),

                        dcc.Graph(
                            id="age-donut-chart",
                            style={"height": "390px"},
                        ),

                    ], className="dashboard-card chart-half"),

                    html.Div([
                        html.H3("Outcome Relationship View"),

                        html.P(
                            "Animal type to outcome breakdown.",
                            className="dashboard-subtitle",
                            style={"textAlign": "center", "marginBottom": "10px"},
                        ),

                        dcc.Graph(
                            id="outcome-sunburst-chart",
                            style={"height": "390px"},
                        ),

                    ], className="dashboard-card chart-half"),

                ], className="analytics-chart-row"),

                # trend chart spans the right column
                html.Div([
                    html.H3("Outcome Trends Over Time"),

                    html.P(
                        "Tracks adoption, transfer, return-to-owner, and total live releases over time.",
                        className="dashboard-subtitle",
                        style={"textAlign": "center", "marginBottom": "10px"},
                    ),

                    dcc.Graph(
                        id="outcome-trend-chart",
                        style={"height": "420px"},
                    ),

                ], className="dashboard-card analytics-trend-card"),

            ], className="analytics-right-column"),

        ], className="analytics-grid"),

    ], className="dashboard-page analytics-page")