from dash import Input, Output, html
import pandas as pd
import plotly.express as px
import dash_leaflet as dl

from services.filters import get_rescue_filter
from breed_utils import normalize_breed, breed_matches


# clean raw records into a dataframe we can work with
def clean_dataframe(records):
    df = pd.DataFrame(records)

    # Mongo adds _id automatically, we do not need it in the UI
    if not df.empty and "_id" in df.columns:
        df = df.drop(columns=["_id"])

    # build a cleaned breed column for filtering + charts
    if not df.empty and "breed" in df.columns:
        df["clean_breed"] = df["breed"].apply(normalize_breed)

    return df


# build the pie chart showing top breeds
def build_breed_pie(data, top_n=8):
    df = pd.DataFrame(data)

    # handle empty data case so the chart does not break
    if df.empty:
        return px.pie(names=["No Data"], values=[1])

    # make sure clean_breed exists before grouping
    if "clean_breed" not in df.columns and "breed" in df.columns:
        df["clean_breed"] = df["breed"].apply(normalize_breed)

    if "clean_breed" not in df.columns:
        return px.pie(names=["No Data"], values=[1])

    # count how often each breed appears
    breed_counts = df["clean_breed"].value_counts()

    # take top breeds and group the rest as "Other"
    top_breeds = breed_counts.head(top_n).copy()

    if len(breed_counts) > top_n:
        other_total = breed_counts.iloc[top_n:].sum()
        top_breeds.loc["Other"] = other_total

    # convert into dataframe for Plotly
    pie_df = pd.DataFrame({
        "breed": top_breeds.index.str.title(),
        "count": top_breeds.values
    })

    # build the pie chart
    figure = px.pie(
        pie_df,
        names="breed",
        values="count",
        title="Top Breed Distribution"
    )

    # small layout tweaks for spacing
    figure.update_layout(
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        legend_title_text="Breed"
    )

    return figure


# clean up animal names so tooltips look consistent
def format_display_name(name):

    if pd.isna(name):
        return "Unnamed Animal"

    name = str(name).strip()

    # remove weird leading characters like *, -, etc.
    while len(name) > 0 and not name[0].isalnum():
        name = name[1:].strip()

    if name == "" or name.lower() == "nan":
        return "Unnamed Animal"

    return name.title()


# build the map marker based on the selected row
def build_map_marker(rows, selected_rows):

    # no data → just return base map
    if not rows:
        return [dl.TileLayer()]

    # default to first row if nothing selected
    if not selected_rows:
        selected_rows = [0]

    row_index = selected_rows[0]
    df = pd.DataFrame(rows)

    # safety check for empty data or bad index
    if df.empty or row_index >= len(df):
        return [dl.TileLayer()]

    row = df.iloc[row_index]

    lat = row.get("location_lat")
    lon = row.get("location_long")

    # pull info for tooltip display
    breed = row.get("clean_breed", row.get("breed", "Unknown Breed"))
    name = format_display_name(row.get("name"))
    outcome = row.get("outcome_type", "Unknown")
    age = row.get("age_upon_outcome", "Unknown")
    color = row.get("color", "Unknown")

    # skip if location is missing
    if pd.isna(lat) or pd.isna(lon):
        return [dl.TileLayer()]

    # build tooltip content
    tooltip_content = html.Div([
        html.B(f"Name: {name}"),
        html.Br(),
        f"Breed: {str(breed).title()}",
        html.Br(),
        f"Outcome: {outcome}",
        html.Br(),
        f"Age: {age}",
        html.Br(),
        f"Color: {color}"
    ])

    return [
        dl.TileLayer(),
        dl.Marker(
            position=[lat, lon],
            children=[
                dl.Tooltip(
                    tooltip_content,
                    direction="top",
                    sticky=True
                ),
                dl.Popup(tooltip_content)
            ]
        )
    ]


# register all dashboard callbacks
def register_callbacks(app, shelter):

    # update table when filters change
    @app.callback(
        Output("datatable-id", "data"),
        Input("filter-type", "value"),
        Input("breed-group-filter", "value")
    )
    def update_table(filter_type, selected_breed):

        # apply rescue filter first
        if filter_type == "all":
            records = shelter.read({})
        else:
            query = get_rescue_filter(filter_type)
            records = shelter.read(query)

        df = clean_dataframe(records)

        # apply breed filter on cleaned breed column
        if selected_breed != "all" and not df.empty:
            df = df[
                df["clean_breed"].apply(
                    lambda x: breed_matches(x, selected_breed)
                )
            ]

        return df.to_dict("records")

    # update pie chart based on table data
    @app.callback(
        Output("pie-chart", "figure"),
        Input("datatable-id", "data")
    )
    def update_pie(data):
        return build_breed_pie(data)

    # update map when a row is selected
    @app.callback(
        Output("map-id", "children"),
        Input("datatable-id", "derived_virtual_data"),
        Input("datatable-id", "derived_virtual_selected_rows")
    )
    def update_map(rows, selected_rows):
        return build_map_marker(rows, selected_rows)

    # show active filters at the top of the page
    @app.callback(
        Output("active-filters", "children"),
        Input("filter-type", "value"),
        Input("breed-group-filter", "value"),
        Input("datatable-id", "data")
    )
    def update_active_filters(filter_type, selected_breed, data):

        filters = []

        if filter_type != "all":
            filters.append(f"Rescue: {filter_type.title()}")

        if selected_breed != "all":
            filters.append(f"Breed: {selected_breed}")

        # build display message
        if not filters:
            message = "Showing all animals"
        else:
            message = " | ".join(filters)

        # show message if no results match filters
        if data is not None and len(data) == 0:
            message += "  —  No matches found. Try selecting 'All' for one filter."

        return message