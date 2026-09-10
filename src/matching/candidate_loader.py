import json


def load_candidate_profile(
    path: str = "data/processed/candidate_profile.json"
) -> dict:

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)