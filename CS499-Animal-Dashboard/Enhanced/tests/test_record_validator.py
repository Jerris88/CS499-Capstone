import unittest

from services.record_validator import RecordValidator


# tests for record validator
class TestRecordValidator(unittest.TestCase):

    def setUp(self):
        self.good_record = {
            "animal_id": "A100001",
            "animal_type": "Dog",
            "breed": "Mixed Breed",
            "sex_upon_outcome": "Intact Female",
            "age_upon_outcome_in_weeks": "40",
            "outcome_type": "Adoption",
            "location_lat": "30.27",
            "location_long": "-97.74",
        }

    # full record should pass validation
    def test_good_record_passes(self):
        is_valid, message = RecordValidator.validate_create_record(self.good_record)

        self.assertTrue(is_valid)
        self.assertEqual(message, "Record is valid.")

    # missing animal id should fail
    def test_missing_animal_id_fails(self):
        record = self.good_record.copy()
        record["animal_id"] = ""

        is_valid, message = RecordValidator.validate_create_record(record)

        self.assertFalse(is_valid)
        self.assertEqual(message, "Animal ID is required.")

    # age has to be a number
    def test_bad_age_fails(self):
        record = self.good_record.copy()
        record["age_upon_outcome_in_weeks"] = "abc"

        is_valid, message = RecordValidator.validate_create_record(record)

        self.assertFalse(is_valid)
        self.assertEqual(message, "Age must be a valid number.")

    # age should not be negative
    def test_negative_age_fails(self):
        record = self.good_record.copy()
        record["age_upon_outcome_in_weeks"] = "-5"

        is_valid, message = RecordValidator.validate_create_record(record)

        self.assertFalse(is_valid)
        self.assertEqual(message, "Age must be zero or higher.")

    # latitude has to stay in range
    def test_bad_latitude_fails(self):
        record = self.good_record.copy()
        record["location_lat"] = "100"

        is_valid, message = RecordValidator.validate_create_record(record)

        self.assertFalse(is_valid)
        self.assertEqual(message, "Latitude must be between -90 and 90.")

    # longitude has to stay in range
    def test_bad_longitude_fails(self):
        record = self.good_record.copy()
        record["location_long"] = "-190"

        is_valid, message = RecordValidator.validate_create_record(record)

        self.assertFalse(is_valid)
        self.assertEqual(message, "Longitude must be between -180 and 180.")

    # blank map values should still be allowed
    def test_blank_location_still_passes(self):
        record = self.good_record.copy()
        record["location_lat"] = ""
        record["location_long"] = ""

        is_valid, message = RecordValidator.validate_create_record(record)

        self.assertTrue(is_valid)
        self.assertEqual(message, "Record is valid.")


if __name__ == "__main__":
    unittest.main()