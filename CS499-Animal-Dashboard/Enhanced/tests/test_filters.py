import re
import unittest

from services.filters import RescueFilters, get_rescue_filter


# tests for rescue filters
class TestRescueFilters(unittest.TestCase):

    # invalid filter should not return a query
    def test_bad_filter_returns_empty(self):
        rescue_filter = get_rescue_filter("not_real")

        self.assertEqual(rescue_filter, {})

    # water filter should include dog and female criteria
    def test_water_filter_has_expected_fields(self):
        rescue_filter = get_rescue_filter("water")

        self.assertEqual(rescue_filter["animal_type"], "Dog")
        self.assertEqual(rescue_filter["sex_upon_outcome"], "Intact Female")
        self.assertIn("breed", rescue_filter)

    # mountain filter should include dog and male criteria
    def test_mountain_filter_has_expected_fields(self):
        rescue_filter = get_rescue_filter("mountain")

        self.assertEqual(rescue_filter["animal_type"], "Dog")
        self.assertEqual(rescue_filter["sex_upon_outcome"], "Intact Male")
        self.assertIn("breed", rescue_filter)

    # disaster filter should use a wider age range
    def test_disaster_filter_has_age_range(self):
        rescue_filter = get_rescue_filter("disaster")

        self.assertEqual(
            rescue_filter["age_upon_outcome_in_weeks"],
            {"$gte": 20, "$lte": 300},
        )

    # breed list should be converted to regex patterns
    def test_breed_query_builds_regex(self):
        breed_query = RescueFilters._breed_query(["Labrador", "Newfoundland"])

        self.assertEqual(len(breed_query), 2)
        self.assertTrue(all(isinstance(item, re.Pattern) for item in breed_query))


if __name__ == "__main__":
    unittest.main()