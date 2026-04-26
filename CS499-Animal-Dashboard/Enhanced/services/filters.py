# rescue filter logic used for dashboard queries

import re


class RescueFilters:

    # base outcomes used across all filters
    BASE_OUTCOMES = {
        "outcome_type": {"$in": ["Adoption", "Transfer", "Return to Owner"]}
    }

    # breed groups for each rescue type
    WATER_BREEDS = [
        "Labrador Retriever Mix",
        "Ches",
        "Newfoundland",
    ]

    MOUNTAIN_BREEDS = [
        "German Shepherd",
        "Alaskan Malamute",
        "Old English Sheepdog",
        "Siberian Husky",
        "Rottweiler",
    ]

    DISASTER_BREEDS = [
        "Doberman Pinscher",
        "German Shepherd",
        "Golden Retriever",
        "Bloodhound",
        "Rottweiler",
    ]

    # build regex queries for breed matching
    @staticmethod
    def _breed_query(breeds):
        return [re.compile(breed, re.IGNORECASE) for breed in breeds]

    # return the correct filter based on type
    @staticmethod
    def get_filter(filter_type):

        if filter_type == "water":
            return {
                **RescueFilters.BASE_OUTCOMES,
                "animal_type": "Dog",
                "breed": {"$in": RescueFilters._breed_query(RescueFilters.WATER_BREEDS)},
                "sex_upon_outcome": "Intact Female",
                "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
            }

        if filter_type == "mountain":
            return {
                **RescueFilters.BASE_OUTCOMES,
                "animal_type": "Dog",
                "breed": {"$in": RescueFilters._breed_query(RescueFilters.MOUNTAIN_BREEDS)},
                "sex_upon_outcome": "Intact Male",
                "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
            }

        if filter_type == "disaster":
            return {
                **RescueFilters.BASE_OUTCOMES,
                "animal_type": "Dog",
                "breed": {"$in": RescueFilters._breed_query(RescueFilters.DISASTER_BREEDS)},
                "sex_upon_outcome": "Intact Male",
                "age_upon_outcome_in_weeks": {"$gte": 20, "$lte": 300},
            }

        return {}


# simple wrapper so other files don’t need to call the class directly
def get_rescue_filter(filter_type):
    return RescueFilters.get_filter(filter_type)