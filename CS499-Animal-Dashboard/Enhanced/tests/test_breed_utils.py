import unittest
import pandas as pd

from breed_utils import (
    normalize_breed,
    get_primary_breed,
    breed_matches,
    get_top_breed_options,
)


# tests for breed utils
class TestBreedUtils(unittest.TestCase):

    # mix text should get removed
    def test_normalize_removes_mix(self):
        breed = normalize_breed("Labrador Retriever Mix")
        self.assertEqual(breed, "labrador retriever")

    # should split on slash and take first breed
    def test_normalize_splits_on_slash(self):
        breed = normalize_breed("German Shepherd/Boxer")
        self.assertEqual(breed, "german shepherd")

    # should handle missing values
    def test_normalize_handles_none(self):
        breed = normalize_breed(None)
        self.assertEqual(breed, "")

    # should format breed name nicely for display
    def test_primary_breed_formats_name(self):
        breed = get_primary_breed("labrador retriever mix")
        self.assertEqual(breed, "Labrador Retriever")

    # should return Unknown if empty
    def test_primary_breed_unknown(self):
        breed = get_primary_breed(None)
        self.assertEqual(breed, "Unknown")

    # same breed should match after cleaning
    def test_breeds_match_after_clean(self):
        match_found = breed_matches("labrador retriever", "Labrador Retriever Mix")
        self.assertTrue(match_found)

    # different breeds should not match
    def test_breeds_do_not_match(self):
        match_found = breed_matches("poodle", "bulldog")
        self.assertFalse(match_found)

    # dropdown should start with All Breeds and include top results
    def test_dropdown_starts_with_all(self):
        df = pd.DataFrame({
            "breed": [
                "Labrador Retriever Mix",
                "Labrador Retriever Mix",
                "German Shepherd",
            ]
        })

        options = get_top_breed_options(df, top_n=2)

        self.assertEqual(options[0], {"label": "All Breeds", "value": "all"})
        self.assertEqual(len(options), 3)

    # empty dataframe should still return default option
    def test_dropdown_handles_empty_df(self):
        df = pd.DataFrame()

        options = get_top_breed_options(df)

        self.assertEqual(options, [{"label": "All Breeds", "value": "all"}])


if __name__ == "__main__":
    unittest.main()