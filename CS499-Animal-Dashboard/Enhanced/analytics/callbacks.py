from dash import Input, Output, html
import pandas as pd
import plotly.express as px

from breed_utils import get_primary_breed


AGE_COLORS = {
    "Baby/Juvenile": "#38bdf8",
    "Young Adult": "#22c55e",
    "Adult": "#f59e0b",
    "Senior": "#a855f7",
    "Unknown": "#64748b",
}

OUTCOME_COLORS = {
    "Adoption": "#059669",
    "Return to Owner": "#2563eb",
    "Transfer": "#f59e0b",
    "Euthanasia": "#dc2626",
    "Other Outcomes": "#64748b",
}

TREND_COLORS = {
    "Adoption": "#059669",
    "Transfer": "#f59e0b",
    "Return to Owner": "#2563eb",
    "Live Release": "#7c3aed",
}


# builds one scorecard for the analytics page
def build_scorecard(title, value, note):
    return html.Div([

        html.H4(title, style={
            "margin": "0 0 5px 0",
            "fontSize": "0.78rem",
            "lineHeight": "1.1",
            "color": "#334155",
        }),

        html.Div(value, style={
            "fontSize": "1.18rem",
            "fontWeight": "700",
            "color": "#0f172a",
            "marginBottom": "4px",
            "lineHeight": "1.05",
        }),

        html.P(note, style={
            "margin": "0",
            "fontSize": "0.66rem",
            "color": "#64748b",
            "lineHeight": "1.18",
        }),

    ], style={
        "background": "rgba(255, 255, 255, 0.72)",
        "border": "1px solid rgba(191, 219, 254, 0.35)",
        "borderRadius": "12px",
        "padding": "10px",
        "boxShadow": "0 5px 14px rgba(30, 41, 59, 0.05)",
        "minHeight": "104px",
    })


# formats metric percentages for display
def format_percent(value):
    if value is None:
        return "N/A"

    return f"{value:.2f}%"


# formats the dominant age bucket card value
def format_age_bucket(metrics):
    bucket = metrics.get("dominant_age_bucket", "Unknown")
    percent = metrics.get("dominant_age_percent", 0)

    return f"{bucket} ({percent:.2f}%)"


# builds the smaller age breakdown note under the age card
def build_age_note(metrics):
    counts = metrics.get("age_bucket_counts", {})

    return (
        f"Baby: {counts.get('Baby/Juvenile', 0):,} | "
        f"Young: {counts.get('Young Adult', 0):,} | "
        f"Adult: {counts.get('Adult', 0):,} | "
        f"Senior: {counts.get('Senior', 0):,}"
    )


# fallback donut when there is no age data
def build_empty_donut(message):
    figure = px.pie(names=[message], values=[1], hole=0.55)

    figure.update_layout(
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 20, "b": 15},
    )

    return figure


# fallback sunburst when there is no outcome data
def build_empty_sunburst(message):
    empty_df = pd.DataFrame({
        "parent": [""],
        "label": [message],
        "count": [1],
    })

    figure = px.sunburst(
        empty_df,
        names="label",
        parents="parent",
        values="count",
    )

    figure.update_layout(
        margin={"l": 15, "r": 15, "t": 20, "b": 15},
    )

    return figure


# fallback line chart when trend data is missing
def build_empty_line_chart(message):
    figure = px.line(title=message)

    figure.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 18},
                "x": 0.5,
                "y": 0.5,
            }
        ],
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
    )

    return figure


# groups less common outcomes together for cleaner charts
def clean_outcome(outcome):
    main_outcomes = [
        "Adoption",
        "Return to Owner",
        "Transfer",
        "Euthanasia",
    ]

    if outcome in main_outcomes:
        return outcome

    return "Other Outcomes"


# groups animal type labels for the sunburst chart
def clean_animal_type(animal_type):
    if animal_type == "Dog":
        return "Dogs"

    if animal_type == "Cat":
        return "Cats"

    return "Other"


# builds the shared animal type query for analytics callbacks
def build_animal_query(animal_type, include_date=False):
    query = {
        "animal_type": {"$exists": True, "$ne": None},
        "outcome_type": {"$exists": True, "$ne": None},
    }

    if include_date:
        query["datetime"] = {"$exists": True, "$ne": None}

    if animal_type == "Other":
        query["animal_type"] = {"$nin": ["Dog", "Cat"]}
    elif animal_type != "All":
        query["animal_type"] = animal_type

    return query


# applies selected breed after records are loaded
def filter_by_breed(df, selected_breed):
    if selected_breed and selected_breed != "All":
        if "breed" not in df.columns:
            return pd.DataFrame()

        df["primary_breed"] = df["breed"].apply(get_primary_breed)
        df = df[df["primary_breed"] == selected_breed]

    return df


# register analytics callbacks
def register_analytics_callbacks(app, shelter):

    # update breed dropdown when animal type changes
    @app.callback(
        Output("analytics-breed-filter", "options"),
        Output("analytics-breed-filter", "value"),
        Input("analytics-animal-type", "value"),
    )
    def update_breed_options(animal_type):
        breeds = shelter.get_breed_options(animal_type)

        options = [{"label": "All Breeds", "value": "All"}]

        for breed in breeds:
            options.append({
                "label": breed,
                "value": breed,
            })

        return options, "All"

    # update summary scorecards
    @app.callback(
        Output("analytics-scorecards", "children"),
        Input("analytics-animal-type", "value"),
        Input("analytics-breed-filter", "value"),
    )
    def update_scorecards(animal_type, selected_breed):
        metrics = shelter.get_outcome_summary_metrics(
            animal_type=animal_type,
            breed=selected_breed,
        )

        return [
            build_scorecard(
                "Total Outcomes",
                f"{metrics['total_outcomes']:,}",
                "Records in selected filter.",
            ),

            build_scorecard(
                "Overall Adoption Rate",
                format_percent(metrics["adoption_rate"]),
                "Adoptions out of all outcomes.",
            ),

            build_scorecard(
                "Live Release Rate",
                format_percent(metrics["live_release_rate"]),
                "Adoption, transfer, and return-to-owner.",
            ),

            build_scorecard(
                "Adoption-to-Euthanasia",
                format_percent(metrics["adoption_vs_euthanasia_rate"]),
                "Adoptions compared with euthanasia.",
            ),

            build_scorecard(
                "Dominant Age Group",
                format_age_bucket(metrics),
                build_age_note(metrics),
            ),

            build_scorecard(
                "Euthanasia Rate",
                format_percent(metrics["euthanasia_rate"]),
                "Euthanasia out of all outcomes.",
            ),

            build_scorecard(
                "Transfer Rate",
                format_percent(metrics["transfer_rate"]),
                "Transfers out of all outcomes.",
            ),

            build_scorecard(
                "Return to Owner Rate",
                format_percent(metrics["return_rate"]),
                "Returned-to-owner outcomes.",
            ),
        ]

    # update age donut chart
    @app.callback(
        Output("age-donut-chart", "figure"),
        Input("analytics-animal-type", "value"),
        Input("analytics-breed-filter", "value"),
    )
    def update_age_donut_chart(animal_type, selected_breed):
        records = shelter.get_age_bucket_distribution(
            animal_type=animal_type,
            breed=selected_breed,
        )

        if not records:
            return build_empty_donut("No Age Data")

        df = pd.DataFrame(records)

        figure = px.pie(
            df,
            names="age_bucket",
            values="count",
            hole=0.55,
            color="age_bucket",
            color_discrete_map=AGE_COLORS,
            category_orders={
                "age_bucket": [
                    "Baby/Juvenile",
                    "Young Adult",
                    "Adult",
                    "Senior",
                    "Unknown",
                ]
            },
        )

        figure.update_traces(
            textposition="inside",
            textinfo="percent+label",
        )

        figure.update_layout(
            margin={"l": 20, "r": 20, "t": 20, "b": 15},
            legend_title_text="Age Category",
        )

        return figure

    # update animal type and outcome sunburst chart
    @app.callback(
        Output("outcome-sunburst-chart", "figure"),
        Input("analytics-animal-type", "value"),
        Input("analytics-breed-filter", "value"),
    )
    def update_outcome_sunburst_chart(animal_type, selected_breed):
        query = build_animal_query(animal_type)
        records = shelter.read(query)
        df = pd.DataFrame(records)

        if df.empty:
            return build_empty_sunburst("No Outcome Data")

        df = filter_by_breed(df, selected_breed)

        if df.empty:
            return build_empty_sunburst("No Outcome Data")

        # clean labels before grouping for the sunburst chart
        df["animal_group"] = df["animal_type"].apply(clean_animal_type)
        df["outcome_group"] = df["outcome_type"].apply(clean_outcome)

        grouped = (
            df.groupby(["animal_group", "outcome_group"])
            .size()
            .reset_index(name="count")
        )

        sunburst_rows = []

        # build parent and child rows for Plotly sunburst
        for animal_group in grouped["animal_group"].unique():
            group_rows = grouped[grouped["animal_group"] == animal_group]
            animal_total = group_rows["count"].sum()

            sunburst_rows.append({
                "label": animal_group,
                "parent": "",
                "count": animal_total,
                "color_group": animal_group,
            })

            for _, row in group_rows.iterrows():
                sunburst_rows.append({
                    "label": f"{animal_group} - {row['outcome_group']}",
                    "parent": animal_group,
                    "count": row["count"],
                    "color_group": row["outcome_group"],
                })

        sunburst_df = pd.DataFrame(sunburst_rows)

        figure = px.sunburst(
            sunburst_df,
            names="label",
            parents="parent",
            values="count",
            color="color_group",
            color_discrete_map=OUTCOME_COLORS,
        )

        figure.update_traces(
            branchvalues="total",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
        )

        figure.update_layout(
            margin={"l": 15, "r": 15, "t": 20, "b": 15},
        )

        return figure

    # update monthly outcome trend chart
    @app.callback(
        Output("outcome-trend-chart", "figure"),
        Input("analytics-animal-type", "value"),
        Input("analytics-breed-filter", "value"),
    )
    def update_outcome_trend_chart(animal_type, selected_breed):
        query = build_animal_query(animal_type, include_date=True)
        records = shelter.read(query)
        df = pd.DataFrame(records)

        if df.empty:
            return build_empty_line_chart("No trend data available.")

        df = filter_by_breed(df, selected_breed)

        if df.empty:
            return build_empty_line_chart("No trend data available for this filter.")

        # convert date text into real datetime values
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df = df[df["datetime"].notna()]

        if df.empty:
            return build_empty_line_chart("No valid date values available.")

        # trend chart focuses on live release outcomes
        df = df[df["outcome_type"].isin([
            "Adoption",
            "Transfer",
            "Return to Owner",
        ])]

        if df.empty:
            return build_empty_line_chart("No live release trend data available.")

        # group records by outcome month
        df["month_period"] = df["datetime"].dt.to_period("M")

        # remove the newest month so partial data does not skew the chart
        latest_month = df["month_period"].max()
        df = df[df["month_period"] < latest_month]

        if df.empty:
            return build_empty_line_chart("No complete month trend data available.")

        df["month"] = df["month_period"].astype(str)

        grouped = (
            df.groupby(["month", "outcome_type"])
            .size()
            .reset_index(name="count")
        )

        pivot = grouped.pivot(
            index="month",
            columns="outcome_type",
            values="count",
        ).fillna(0)

        # make sure each live release column exists before adding them together
        for column in ["Adoption", "Transfer", "Return to Owner"]:
            if column not in pivot.columns:
                pivot[column] = 0

        pivot["Live Release"] = (
            pivot["Adoption"] +
            pivot["Transfer"] +
            pivot["Return to Owner"]
        )

        pivot = pivot.reset_index()

        figure = px.line(
            pivot,
            x="month",
            y=[
                "Adoption",
                "Transfer",
                "Return to Owner",
                "Live Release",
            ],
            markers=True,
            color_discrete_map=TREND_COLORS,
        )

        figure.update_layout(
            margin={"l": 30, "r": 20, "t": 20, "b": 70},
            legend_title_text="Outcome Type",
            xaxis_title="Outcome Month",
            yaxis_title="Outcome Count",
        )

        figure.update_xaxes(
            tickangle=-45,
            nticks=12,
        )

        return figure