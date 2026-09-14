import json

from src.database.connection import get_connection
from src.matching.semantic_matcher import calculate_semantic_components


def load_candidate_profile():
    with open(
        "data/processed/candidate_profile.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def build_candidate_experience(profile):
    return " ".join(
        f"{item.get('role', '')} at {item.get('organization', '')}. "
        f"{item.get('description', '')}"
        for item in profile.get("experience", [])
    )


def build_candidate_projects(profile):
    return " ".join(
        f"{item.get('name', '')}. "
        f"Technologies: {', '.join(item.get('technologies', []))}. "
        f"{item.get('description', '')}"
        for item in profile.get("projects", [])
    )


def get_test_jobs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT title, company, description, skills
        FROM jobs
        WHERE title IN (
            'Software Engineer, Backend',
            'Visual Designer, Web'
        )
        ORDER BY title;
    """)

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return jobs


profile = load_candidate_profile()

candidate_skills = profile.get("skills", [])
candidate_experience = build_candidate_experience(profile)
candidate_projects = build_candidate_projects(profile)

jobs = get_test_jobs()

if not jobs:
    print("Test jobs not found.")
else:
    print("\n===== SEMANTIC COMPARISON TEST =====")

    for title, company, description, job_skills in jobs:

        result = calculate_semantic_components(
            candidate_skills=candidate_skills,
            candidate_experience=candidate_experience,
            candidate_projects=candidate_projects,
            job_skills=job_skills or [],
            job_description=description or ""
        )

        print("\n" + "=" * 55)
        print("Job:", title)
        print("Company:", company)

        print("\nSkill similarity:",
              result["skill_similarity"])

        print("Experience similarity:",
              result["experience_similarity"])

        print("Project similarity:",
              result["project_similarity"])

        print("Semantic score:",
              result["semantic_score"])