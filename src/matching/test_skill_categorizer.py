import json

from src.matching.skill_categorizer import categorize_skills


def main():

    with open(
        "data/processed/candidate_profile.json",
        "r",
        encoding="utf-8"
    ) as file:

        candidate = json.load(file)

    categorized = categorize_skills(
        candidate["skills"]
    )

    print("\n===== CANDIDATE SKILL CATEGORIES =====")

    for category, skills in categorized.items():

        print(f"\n{category}:")
        print(skills)


if __name__ == "__main__":
    main()