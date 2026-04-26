from dash import Input, Output, State, no_update
from services.record_validator import RecordValidator


# registers callback for creating new records
def register_create_callbacks(app, shelter):

    # ======================
    # CREATE NEW RECORD
    # ======================
    @app.callback(
        Output("create-output", "children"),
        Output("create-output", "className"),
        Output("create-animal-id", "value"),
        Output("create-name", "value"),
        Output("create-animal-type", "value"),
        Output("create-breed", "value"),
        Output("create-color", "value"),
        Output("create-sex-upon-outcome", "value"),
        Output("create-age-upon-outcome-in-weeks", "value"),
        Output("create-outcome-type", "value"),
        Output("create-location-lat", "value"),
        Output("create-location-long", "value"),
        Input("btn-create", "n_clicks"),
        State("create-animal-id", "value"),
        State("create-name", "value"),
        State("create-animal-type", "value"),
        State("create-breed", "value"),
        State("create-color", "value"),
        State("create-sex-upon-outcome", "value"),
        State("create-age-upon-outcome-in-weeks", "value"),
        State("create-outcome-type", "value"),
        State("create-location-lat", "value"),
        State("create-location-long", "value"),
        prevent_initial_call=True,
    )
    def create_record(
        n_clicks,
        animal_id,
        name,
        animal_type,
        breed,
        color,
        sex_upon_outcome,
        age_upon_outcome_in_weeks,
        outcome_type,
        location_lat,
        location_long,
    ):

        if not n_clicks:
            return no_update

        # collect form values into one record
        record = {
            "animal_id": animal_id,
            "name": name,
            "animal_type": animal_type,
            "breed": breed,
            "color": color,
            "sex_upon_outcome": sex_upon_outcome,
            "age_upon_outcome_in_weeks": age_upon_outcome_in_weeks,
            "outcome_type": outcome_type,
            "location_lat": location_lat,
            "location_long": location_long,
        }

        # validate required fields and numeric values before saving
        is_valid, message = RecordValidator.validate_create_record(record)

        if not is_valid:
            return (
                message,
                "admin-message error",
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
            )

        # animal id should stay unique
        existing_record = shelter.read({"animal_id": animal_id})

        if existing_record:
            return (
                "That animal ID already exists. Please use a unique ID.",
                "admin-message error",
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
            )

        success = shelter.create(record)

        if success:
            return (
                f"Record {animal_id} created successfully.",
                "admin-message success",
                "", "", "", "", "", "", "", "", "", "",
            )

        return (
            "Create failed.",
            "admin-message error",
            no_update, no_update, no_update, no_update, no_update,
            no_update, no_update, no_update, no_update, no_update,
        )