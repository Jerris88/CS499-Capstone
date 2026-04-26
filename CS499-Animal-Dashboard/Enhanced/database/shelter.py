from pymongo import MongoClient
from pymongo.errors import PyMongoError


# handles animal records and analytics queries
class AnimalShelter:

    def __init__(
        self,
        user="",
        pwd="",
        host="localhost",
        port=27017,
        db="AAC",
        collection="animals",
    ):
        self.client = self.connect(user, pwd, host, port)
        self.database = self.client[db]
        self.collection = self.database[collection]

    # connect to MongoDB
    def connect(self, user, pwd, host, port):
        try:
            if user and pwd:
                return MongoClient(f"mongodb://{user}:{pwd}@{host}:{port}")

            return MongoClient(f"mongodb://{host}:{port}")

        except PyMongoError as e:
            print("Error connecting to MongoDB:", e)
            return None

    # add one record
    def create(self, data):
        if not data:
            raise ValueError("Nothing to save, because data parameter is empty.")

        try:
            self.collection.insert_one(data)
            return True
        except PyMongoError as e:
            print("An error occurred while attempting to add data:", e)
            return False

    # read records that match the query
    def read(self, query=None):
        try:
            results = self.collection.find(query or {})
            return list(results)
        except PyMongoError as e:
            print("An error occurred while attempting to read data:", e)
            return []

    # update records that match the query
    def update(self, query, data):
        if not query:
            raise ValueError("Error: search parameter is empty.")
        if not data:
            raise ValueError("Nothing to update, because data parameter is empty.")

        try:
            results = self.collection.update_many(query, {"$set": data})
            return results.modified_count
        except PyMongoError as e:
            print("An error occurred while attempting to update data:", e)
            return 0

    # delete records that match the query
    def delete(self, query):
        if not query:
            raise ValueError("Error: search parameter is empty.")

        try:
            results = self.collection.delete_many(query)
            return results.deleted_count
        except PyMongoError as e:
            print("An error occurred while attempting to delete data:", e)
            return 0

    # ======================
    # Analytics Helpers
    # ======================

    # normalize breed text from MongoDB
    def build_clean_breed(self):

        # take the first breed if multiple breeds are listed
        first_breed = {
            "$arrayElemAt": [
                {"$split": ["$breed", "/"]},
                0,
            ]
        }

        # remove Mix with a capital M
        remove_upper_mix = {
            "$replaceAll": {
                "input": first_breed,
                "find": " Mix",
                "replacement": "",
            }
        }

        # remove mix with a lowercase m if the text is inconsistent
        remove_lower_mix = {
            "$replaceAll": {
                "input": remove_upper_mix,
                "find": " mix",
                "replacement": "",
            }
        }

        # trim spaces after the breed text is cleaned
        return {
            "$trim": {
                "input": remove_lower_mix
            }
        }

    # simplify outcome labels for charts
    def build_outcome_group(self):

        # these are the outcome groups shown directly in the chart
        outcome_groups = [
            ("Adoption", "Adoption"),
            ("Return to Owner", "Return to Owner"),
            ("Transfer", "Transfer"),
            ("Euthanasia", "Euthanasia"),
        ]

        # anything outside the main groups gets rolled into Other Outcomes
        return {
            "$switch": {
                "branches": [
                    {
                        "case": {"$eq": ["$outcome_type", outcome]},
                        "then": label,
                    }
                    for outcome, label in outcome_groups
                ],
                "default": "Other Outcomes",
            }
        }

    # convert raw age in weeks into chart buckets
    def build_age_bucket(self):

        # younger than 26 weeks
        baby = {"$lt": ["$age_upon_outcome_in_weeks", 26]}

        # 26 weeks up to 104 weeks
        young_adult = {
            "$and": [
                {"$gte": ["$age_upon_outcome_in_weeks", 26]},
                {"$lt": ["$age_upon_outcome_in_weeks", 104]},
            ]
        }

        # 104 weeks up to 364 weeks
        adult = {
            "$and": [
                {"$gte": ["$age_upon_outcome_in_weeks", 104]},
                {"$lt": ["$age_upon_outcome_in_weeks", 364]},
            ]
        }

        # 364 weeks and older
        senior = {"$gte": ["$age_upon_outcome_in_weeks", 364]}

        # MongoDB checks the age ranges in order and returns the first match
        return {
            "$switch": {
                "branches": [
                    {"case": baby, "then": "Baby/Juvenile"},
                    {"case": young_adult, "then": "Young Adult"},
                    {"case": adult, "then": "Adult"},
                    {"case": senior, "then": "Senior"},
                ],
                "default": "Unknown",
            }
        }

    # shared animal type filter for analytics
    def build_base_match(self, animal_type="All"):

        # all analytics views need basic outcome and animal type data
        match_query = {
            "outcome_type": {"$exists": True, "$ne": None},
            "animal_type": {"$exists": True, "$ne": None},
        }

        # Other is used for anything outside Dog and Cat
        if animal_type == "Other":
            match_query["animal_type"] = {"$nin": ["Dog", "Cat"]}

        # Dog or Cat filters are applied directly
        elif animal_type != "All":
            match_query["animal_type"] = animal_type

        return match_query

    # count records when a field equals a value
    def count_matches(self, field_name, value):
        return {
            "$sum": {
                "$cond": [
                    {"$eq": [f"${field_name}", value]},
                    1,
                    0,
                ]
            }
        }

    # count one outcome type
    def count_outcome(self, outcome_type):
        return self.count_matches("outcome_type", outcome_type)

    # convert a Mongo count expression into a percentage
    def build_percent(self, top_value, bottom_value="$total"):
        return {
            "$round": [
                {
                    "$multiply": [
                        {"$divide": [top_value, bottom_value]},
                        100,
                    ]
                },
                2,
            ]
        }

    # keep scorecard fallback values in one place
    def empty_summary_metrics(self):
        return {
            "total_outcomes": 0,
            "adoption_rate": 0,
            "live_release_rate": 0,
            "return_rate": 0,
            "transfer_rate": 0,
            "euthanasia_rate": 0,
            "adoption_vs_euthanasia_rate": None,
            "dominant_age_bucket": "Unknown",
            "dominant_age_percent": 0,
            "age_bucket_counts": {
                "Baby/Juvenile": 0,
                "Young Adult": 0,
                "Adult": 0,
                "Senior": 0,
                "Unknown": 0,
            },
        }

    # find the biggest age bucket after Mongo returns the counts
    def get_dominant_age(self, age_counts, total):

        # pick the age bucket with the largest count
        dominant_bucket = max(age_counts, key=age_counts.get)
        dominant_count = age_counts.get(dominant_bucket, 0)

        # convert the dominant count into a percent of total outcomes
        if total > 0:
            dominant_percent = round((dominant_count / total) * 100, 2)
        else:
            dominant_percent = 0

        return dominant_bucket, dominant_percent

    # ======================
    # Breed Options
    # ======================

    # get cleaned breed names for the analytics dropdown
    def get_breed_options(self, animal_type="All"):
        match_query = self.build_base_match(animal_type)

        # breed has to exist before it can be cleaned or grouped
        match_query["breed"] = {"$exists": True, "$ne": None}

        pipeline = [
            # start with records matching the animal type filter
            {"$match": match_query},

            # add a cleaned breed field before grouping
            {
                "$addFields": {
                    "primary_breed": self.build_clean_breed(),
                }
            },

            # skip blank breed values after cleanup
            {
                "$match": {
                    "primary_breed": {"$ne": ""},
                }
            },

            # group by cleaned breed name
            {
                "$group": {
                    "_id": "$primary_breed",
                    "count": {"$sum": 1},
                }
            },

            # sort so the dropdown is easier to scan
            {
                "$sort": {
                    "_id": 1,
                }
            },
        ]

        try:
            results = list(self.collection.aggregate(pipeline))

            # only return the breed names because the dropdown does not need counts
            return [
                item["_id"]
                for item in results
                if item.get("_id")
            ]

        except PyMongoError as e:
            print("Error loading breed options:", e)
            return []

    # ======================
    # Scorecard Metrics
    # ======================

    # get the main scorecard numbers for the analytics page
    def get_outcome_summary_metrics(self, animal_type="All", breed="All"):
        match_query = self.build_base_match(animal_type)

        pipeline = [
            # use records with basic outcome and animal type data
            {"$match": match_query},

            # add fields needed for breed filtering and age grouping
            {
                "$addFields": {
                    "primary_breed": self.build_clean_breed(),
                    "age_bucket": self.build_age_bucket(),
                }
            },
        ]

        # breed filtering happens after the cleaned breed field is created
        if breed and breed != "All":
            pipeline.append({
                "$match": {
                    "primary_breed": breed,
                }
            })

        pipeline.extend([
            # count totals, outcomes, and age bucket groups
            {
                "$group": {
                    "_id": None,

                    # total records after filters are applied
                    "total": {"$sum": 1},

                    # outcome counts used to calculate scorecard rates
                    "adopted": self.count_outcome("Adoption"),
                    "returned": self.count_outcome("Return to Owner"),
                    "transferred": self.count_outcome("Transfer"),
                    "euthanized": self.count_outcome("Euthanasia"),

                    # age bucket counts used for the dominant age card
                    "baby_juvenile_count": self.count_matches(
                        "age_bucket",
                        "Baby/Juvenile",
                    ),
                    "young_adult_count": self.count_matches(
                        "age_bucket",
                        "Young Adult",
                    ),
                    "adult_count": self.count_matches("age_bucket", "Adult"),
                    "senior_count": self.count_matches("age_bucket", "Senior"),
                    "unknown_age_count": self.count_matches("age_bucket", "Unknown"),
                }
            },

            # calculate the rates shown in the scorecards
            {
                "$project": {
                    "_id": 0,
                    "total": 1,

                    # keep raw age counts so Python can find the largest bucket
                    "baby_juvenile_count": 1,
                    "young_adult_count": 1,
                    "adult_count": 1,
                    "senior_count": 1,
                    "unknown_age_count": 1,

                    # each rate is count divided by total outcomes
                    "adoption_rate": self.build_percent("$adopted"),
                    "return_rate": self.build_percent("$returned"),
                    "transfer_rate": self.build_percent("$transferred"),
                    "euthanasia_rate": self.build_percent("$euthanized"),

                    # live release combines positive non-euthanasia outcomes
                    "live_release_rate": self.build_percent({
                        "$add": [
                            "$adopted",
                            "$returned",
                            "$transferred",
                        ]
                    }),

                    # this compares adoption against euthanasia only
                    "adoption_vs_euthanasia_rate": {
                        "$cond": [
                            {
                                "$eq": [
                                    {"$add": ["$adopted", "$euthanized"]},
                                    0,
                                ]
                            },
                            None,
                            self.build_percent(
                                "$adopted",
                                {"$add": ["$adopted", "$euthanized"]},
                            ),
                        ]
                    },
                }
            },
        ])

        try:
            result = list(self.collection.aggregate(pipeline))

            # no records means the cards still need safe default values
            if not result:
                return self.empty_summary_metrics()

            data = result[0]
            total = data.get("total", 0)

            # keep age counts together for display and dominant age logic
            age_counts = {
                "Baby/Juvenile": data.get("baby_juvenile_count", 0),
                "Young Adult": data.get("young_adult_count", 0),
                "Adult": data.get("adult_count", 0),
                "Senior": data.get("senior_count", 0),
                "Unknown": data.get("unknown_age_count", 0),
            }

            # find which age bucket appears most often
            dominant_age_bucket, dominant_age_percent = self.get_dominant_age(
                age_counts,
                total,
            )

            return {
                "total_outcomes": total,
                "adoption_rate": data.get("adoption_rate", 0),
                "live_release_rate": data.get("live_release_rate", 0),
                "return_rate": data.get("return_rate", 0),
                "transfer_rate": data.get("transfer_rate", 0),
                "euthanasia_rate": data.get("euthanasia_rate", 0),
                "adoption_vs_euthanasia_rate": data.get(
                    "adoption_vs_euthanasia_rate"
                ),
                "dominant_age_bucket": dominant_age_bucket,
                "dominant_age_percent": dominant_age_percent,
                "age_bucket_counts": age_counts,
            }

        except PyMongoError as e:
            print("Error calculating summary metrics:", e)
            return self.empty_summary_metrics()

    # ======================
    # Age Donut Chart
    # ======================

    # get age bucket counts for the donut chart
    def get_age_bucket_distribution(self, animal_type="All", breed="All"):
        match_query = self.build_base_match(animal_type)

        # donut chart only needs records that have age data
        match_query["age_upon_outcome_in_weeks"] = {"$exists": True, "$ne": None}

        pipeline = [
            # only use records with age data
            {"$match": match_query},

            # add cleaned breed and age bucket fields
            {
                "$addFields": {
                    "primary_breed": self.build_clean_breed(),
                    "age_bucket": self.build_age_bucket(),
                }
            },
        ]

        # apply selected breed if the user picks one
        if breed and breed != "All":
            pipeline.append({
                "$match": {
                    "primary_breed": breed,
                }
            })

        pipeline.extend([
            # count how many records fall into each age bucket
            {
                "$group": {
                    "_id": "$age_bucket",
                    "count": {"$sum": 1},
                }
            },

            # show the largest bucket first
            {
                "$sort": {
                    "count": -1,
                }
            },
        ])

        try:
            results = list(self.collection.aggregate(pipeline))

            # reshape Mongo results into a chart-friendly list
            return [
                {
                    "age_bucket": item.get("_id", "Unknown"),
                    "count": item.get("count", 0),
                }
                for item in results
            ]

        except PyMongoError as e:
            print("Error loading age bucket distribution:", e)
            return []

    # ======================
    # Outcome Distribution
    # ======================

    # group smaller breeds so the chart stays readable
    def build_chart_breed(self, min_count):

        # breeds below the minimum count are combined into Other/Mixed
        return {
            "$cond": [
                {"$lt": ["$total", min_count]},
                "Other/Mixed",
                "$_id",
            ]
        }

    # count one outcome from the grouped outcome field
    def count_grouped_outcome(self, outcome_name):
        return {
            "$sum": {
                "$cond": [
                    {"$eq": ["$_id.outcome", outcome_name]},
                    "$count",
                    0,
                ]
            }
        }

    # get outcome percentages by breed
    def get_outcome_distribution_by_breed(self, animal_type="All", min_count=5):
        match_query = self.build_base_match(animal_type)

        # breed is required because this chart groups outcomes by breed
        match_query["breed"] = {"$exists": True, "$ne": None}

        pipeline = [
            # start with records that have the needed fields
            {"$match": match_query},

            # clean breed names and group smaller outcome labels
            {
                "$addFields": {
                    "primary_breed": self.build_clean_breed(),
                    "outcome_group": self.build_outcome_group(),
                }
            },

            # count each outcome type within each breed
            {
                "$group": {
                    "_id": {
                        "breed": "$primary_breed",
                        "outcome": "$outcome_group",
                    },
                    "count": {"$sum": 1},
                }
            },

            # collect each breed into one record with total and outcome list
            {
                "$group": {
                    "_id": "$_id.breed",

                    # total number of outcomes for the breed
                    "total": {"$sum": "$count"},

                    # keep the outcome breakdown so it can be regrouped later
                    "outcomes": {
                        "$push": {
                            "outcome": "$_id.outcome",
                            "count": "$count",
                        }
                    },
                }
            },

            # small breed counts get grouped as Other/Mixed
            {
                "$addFields": {
                    "chart_breed": self.build_chart_breed(min_count),
                }
            },

            # unwind so Mongo can regroup after combining small breeds
            {"$unwind": "$outcomes"},

            # regroup with chart breed name instead of original breed name
            {
                "$group": {
                    "_id": {
                        "breed": "$chart_breed",
                        "outcome": "$outcomes.outcome",
                    },
                    "count": {"$sum": "$outcomes.count"},
                }
            },

            # build one row per breed with counts for each outcome type
            {
                "$group": {
                    "_id": "$_id.breed",

                    # total outcomes for this chart breed
                    "total": {"$sum": "$count"},

                    # each one becomes a separate count field for the chart
                    "adoption_count": self.count_grouped_outcome("Adoption"),
                    "return_count": self.count_grouped_outcome("Return to Owner"),
                    "transfer_count": self.count_grouped_outcome("Transfer"),
                    "euthanasia_count": self.count_grouped_outcome("Euthanasia"),
                    "other_count": self.count_grouped_outcome("Other Outcomes"),
                }
            },

            # convert counts into rates for the chart
            {
                "$project": {
                    "_id": 0,
                    "breed": "$_id",
                    "total": 1,
                    "adoption_count": 1,
                    "return_count": 1,
                    "transfer_count": 1,
                    "euthanasia_count": 1,
                    "other_count": 1,

                    # each chart segment uses a percent instead of raw count
                    "adoption_rate": self.build_percent("$adoption_count"),
                    "return_rate": self.build_percent("$return_count"),
                    "transfer_rate": self.build_percent("$transfer_count"),
                    "euthanasia_rate": self.build_percent("$euthanasia_count"),
                    "other_rate": self.build_percent("$other_count"),
                }
            },

            # biggest breed groups show first
            {"$sort": {"total": -1}},
        ]

        baseline_pipeline = [
            # use the same filter so the baseline matches the chart
            {"$match": match_query},

            # count total records and total adoptions
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "adopted": self.count_outcome("Adoption"),
                }
            },

            # calculate shelter-wide adoption rate
            {
                "$project": {
                    "_id": 0,
                    "average_adoption_rate": self.build_percent("$adopted"),
                }
            },
        ]

        try:
            chart_data = list(self.collection.aggregate(pipeline))
            baseline_data = list(self.collection.aggregate(baseline_pipeline))

            average_adoption_rate = 0

            # baseline may be empty if there is no matching data
            if baseline_data:
                average_adoption_rate = baseline_data[0].get(
                    "average_adoption_rate",
                    0,
                )

            return {
                "chart_data": chart_data,
                "average_adoption_rate": average_adoption_rate,
            }

        except PyMongoError as e:
            print("An error occurred while aggregating analytics data:", e)
            return {
                "chart_data": [],
                "average_adoption_rate": 0,
            }