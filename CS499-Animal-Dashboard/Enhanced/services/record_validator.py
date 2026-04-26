# checks if a record is valid before adding it to the database


class RecordValidator:

    REQUIRED_FIELDS = {
        "animal_id": "Animal ID",
        "animal_type": "Animal Type",
        "breed": "Breed",
        "sex_upon_outcome": "Sex Upon Outcome",
        "age_upon_outcome_in_weeks": "Age Upon Outcome",
        "outcome_type": "Outcome Type",
    }

    # basic validation for required fields and numbers
    @staticmethod
    def validate_create_record(record):

        # make sure required fields are filled in
        for field, label in RecordValidator.REQUIRED_FIELDS.items():
            if record.get(field) in [None, ""]:
                return False, f"{label} is required."

        # check age
        try:
            age = float(record["age_upon_outcome_in_weeks"])
            if age < 0:
                return False, "Age must be zero or higher."
        except (TypeError, ValueError):
            return False, "Age must be a valid number."

        lat = record.get("location_lat")
        lon = record.get("location_long")

        # latitude is optional but needs to be valid if entered
        if lat not in [None, ""]:
            try:
                lat = float(lat)
                if lat < -90 or lat > 90:
                    return False, "Latitude must be between -90 and 90."
            except (TypeError, ValueError):
                return False, "Latitude must be a valid number."

        # longitude is optional but needs to be valid if entered
        if lon not in [None, ""]:
            try:
                lon = float(lon)
                if lon < -180 or lon > 180:
                    return False, "Longitude must be between -180 and 180."
            except (TypeError, ValueError):
                return False, "Longitude must be a valid number."

        return True, "Record is valid."