import json

from src.database.connection import get_connection
from src.matching.semantic_matcher import calculate_semantic_score


def load_candidate_profile():
    with open(
        "data/processed/candidate_profile.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def build_candidate_text(profile):
    skills = ", ".join(profile.get("skills", []))
    target_roles = ", ".join(profile.get("target_roles", []))

    return f"""
    Candidate skills: {skills}

    Target roles: {target_roles}
    """


def get_one_job():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT title, company, description
        FROM jobs
        WHERE title = 'Software Engineer, Backend'
        LIMIT 1;
    """)

    job = cursor.fetchone()

    cursor.close()
    connection.close()

    return job


profile = load_candidate_profile()

candidate_text = build_candidate_text(profile)

job = get_one_job()

if job is None:
    print("Job not found.")
else:
    title, company, description = job

    job_text = f"""
    Job title: {title}
    Company: {company}

    Job description:
    {description}
    """

    score = calculate_semantic_score(
        candidate_text,
        job_text
    )

    print("\n===== SEMANTIC MATCH TEST =====")
    print("Job:", title)
    print("Company:", company)
    print("Semantic score:", score)