import unittest
from database.shelter import AnimalShelter


# tests for shelter database class
class TestAnimalShelter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # set up connection to local MongoDB
        cls.shelter = AnimalShelter(
            user="",
            pwd="",
            host="localhost",
            port=27017,
            db="AAC",
            collection="animals",
        )

    # read should always return a list
    def test_read_returns_list(self):
        results = self.shelter.read({})
        self.assertIsInstance(results, list)

    # local database should have records loaded
    def test_read_all_has_data(self):
        results = self.shelter.read({})
        self.assertTrue(len(results) > 0)

    # create should not accept empty data
    def test_create_empty_raises_error(self):
        with self.assertRaises(ValueError):
            self.shelter.create({})

    # update needs a query filter
    def test_update_empty_query_raises_error(self):
        with self.assertRaises(ValueError):
            self.shelter.update({}, {"name": "Test"})

    # delete needs a query filter
    def test_delete_empty_query_raises_error(self):
        with self.assertRaises(ValueError):
            self.shelter.delete({})

    # create and delete a small test record
    def test_create_and_delete_record(self):
        test_data = {
            "animal_id": "TEST100",
            "animal_type": "Dog",
            "breed": "Mixed Breed",
            "sex_upon_outcome": "Intact Female",
            "age_upon_outcome_in_weeks": 40,
            "outcome_type": "Adoption",
        }

        created = self.shelter.create(test_data)
        self.assertTrue(created)

        results = self.shelter.read({"animal_id": "TEST100"})
        self.assertTrue(len(results) > 0)

        deleted_count = self.shelter.delete({"animal_id": "TEST100"})
        self.assertGreater(deleted_count, 0)

    # All should only require the shared analytics fields
    def test_base_match_all(self):
        match_query = self.shelter.build_base_match("All")

        self.assertIn("outcome_type", match_query)
        self.assertIn("animal_type", match_query)

    # Other should exclude dog and cat records
    def test_base_match_other(self):
        match_query = self.shelter.build_base_match("Other")

        self.assertEqual(match_query["animal_type"], {"$nin": ["Dog", "Cat"]})

    # Dog should filter directly by animal type
    def test_base_match_dog(self):
        match_query = self.shelter.build_base_match("Dog")

        self.assertEqual(match_query["animal_type"], "Dog")

    # empty summary keeps analytics page from breaking
    def test_empty_summary_metrics(self):
        metrics = self.shelter.empty_summary_metrics()

        self.assertEqual(metrics["total_outcomes"], 0)
        self.assertEqual(metrics["dominant_age_bucket"], "Unknown")
        self.assertIsNone(metrics["adoption_vs_euthanasia_rate"])

    # dominant age should return the largest age bucket
    def test_get_dominant_age(self):
        age_counts = {
            "Baby/Juvenile": 2,
            "Young Adult": 8,
            "Adult": 4,
            "Senior": 1,
            "Unknown": 0,
        }

        bucket, percent = self.shelter.get_dominant_age(age_counts, 15)

        self.assertEqual(bucket, "Young Adult")
        self.assertEqual(percent, 53.33)

    # helper should build a Mongo percentage expression
    def test_build_percent_returns_expression(self):
        percent_expr = self.shelter.build_percent("$adopted")

        self.assertIn("$round", percent_expr)

    # helper should build a Mongo count expression
    def test_count_matches_returns_expression(self):
        count_expr = self.shelter.count_matches("age_bucket", "Adult")

        self.assertIn("$sum", count_expr)


if __name__ == "__main__":
    unittest.main()