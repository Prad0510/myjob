import os
from dotenv import load_dotenv

load_dotenv()
import json

from src.database.connection import get_connection
from src.matching.job_matcher import match_job
from src.matching.eligibility_filter import classify_eligibility

MATCH_THRESHOLD = float(
    os.getenv("MATCH_THRESHOLD", 75)
)

def load_candidate_skills():

    with open(
        "data/processed/candidate_profile.json",
        "r",
        encoding="utf-8"
    ) as file:
        candidate = json.load(file)

    return candidate["skills"]


def evaluate_jobs():

    candidate_skills = load_candidate_skills()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            company,
            location,
            skills,
            experience_required
        FROM jobs
        ORDER BY id;
    """)

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    results = []

    for (
        job_id,
        title,
        company,
        location,
        job_skills,
        experience_required
    ) in jobs:

        job_skills = job_skills or []
        
        eligibility = classify_eligibility(
        title,
        experience_required or ""
    )

        if eligibility == "not_eligible":
            continue

        match_result = match_job(
            candidate_skills,
            title,
            job_skills,
            experience_required or ""
        )

        results.append({
            "job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "eligibility": eligibility,
            "skill_score": match_result["skill_score"],
            "role_score": match_result["role_score"],
            "experience_score": match_result["experience_score"],
            "final_score": match_result["final_score"],
            "matched_skills": match_result.get(
                "matched_skills", []
            ),
            "missing_skills": match_result.get(
                "missing_skills", []
            ),
        })

    # Highest final score first
    eligibility_priority = {
    "eligible": 2,
    "uncertain": 1,
    "not_eligible": 0
    }

    results.sort(
    key=lambda job: (
        eligibility_priority[job["eligibility"]],
        job["final_score"]
    ),
    reverse=True
)   
    matching_jobs = [
    job
    for job in results
    if job["final_score"] >= MATCH_THRESHOLD
]
    print("\n===== JOBS ABOVE THRESHOLD =====")

    print(
    f"Match threshold: {MATCH_THRESHOLD}%"
    )
    for job in matching_jobs:

        print("\n" + "=" * 60)

        print(
            f'{job["title"]} '
            f'({job["company"]})'
        )

        print(
            f'Final score: '
            f'{job["final_score"]}%'
        )

        print(
            f'Skill score: '
            f'{job["skill_score"]}%'
        )

        print(
            f'Role score: '
            f'{job["role_score"]}%'
        )

        print(
            f'Experience score: '
            f'{job["experience_score"]}%'
        )

        print(
            f'Matched: '
            f'{job["matched_skills"]}'
        )

        print(
            f'Missing: '
            f'{job["missing_skills"]}'
        )
        
        print(
    f'Eligibility: '
    f'{job["eligibility"]}'
)


if __name__ == "__main__":
    evaluate_jobs()