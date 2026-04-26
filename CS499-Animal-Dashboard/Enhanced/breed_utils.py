# breed normalization and matching helpers for the shelter dashboard
# cleans messy breed text so filtering works more consistently

import pandas as pd


# normalize breed text from database
def normalize_breed(breed):

    if pd.isna(breed):
        return ""

    breed = str(breed).lower()
    breed = breed.split("/")[0]          # take first breed if multiple are listed
    breed = breed.replace(" mix", "")
    breed = breed.replace("mix", "")
    breed = breed.strip()

    return breed


# get main breed name for display
def get_primary_breed(breed):

    clean_breed = normalize_breed(breed)

    if not clean_breed:
        return "Unknown"

    return clean_breed.title()


# check if two breeds match after cleaning
def breed_matches(clean_breed, selected_breed):

    if not clean_breed or not selected_breed:
        return False

    return normalize_breed(selected_breed) == normalize_breed(clean_breed)


# build dropdown options from most common breeds
def get_top_breed_options(df, top_n=15):

    if df.empty or "breed" not in df.columns:
        return [{"label": "All Breeds", "value": "all"}]

    clean_breeds = df["breed"].apply(get_primary_breed)
    top_breeds = clean_breeds.value_counts().head(top_n).index.tolist()

    options = [{"label": "All Breeds", "value": "all"}]

    for breed in top_breeds:
        options.append({"label": breed, "value": breed})

    return options