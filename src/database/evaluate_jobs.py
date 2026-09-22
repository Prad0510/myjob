import os
from dotenv import load_dotenv

load_dotenv()
import json
from src.database.match_repository import save_match
from src.database.connection import get_connection
from src.matching.job_matcher import match_job
from src.matching.eligibility_filter import classify_eligibility
from src.notifications.telegram import send_telegram_message
from src.database.match_repository import save_match

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

def load_target_roles():
    with open(
        "data/processed/candidate_profile.json",
        "r",
        encoding="utf-8"
    ) as file:

        candidate_data = json.load(file)

    return candidate_data.get(
        "target_roles",
        []
    )
    
def load_candidate_experience():
    with open(
        "data/processed/candidate_profile.json",
        "r",
        encoding="utf-8"
    ) as file:
        candidate_data = json.load(file)

    experience = candidate_data.get("experience", [])

    return " ".join(
        f"{item.get('role', '')} at {item.get('organization', '')}. "
        f"{item.get('description', '')}"
        for item in experience
    )


def load_candidate_projects():
    with open(
        "data/processed/candidate_profile.json",
        "r",
        encoding="utf-8"
    ) as file:
        candidate_data = json.load(file)

    projects = candidate_data.get("projects", [])

    return " ".join(
        f"{item.get('name', '')}. "
        f"Technologies: {', '.join(item.get('technologies', []))}. "
        f"{item.get('description', '')}"
        for item in projects
    )

def evaluate_jobs(job_ids):

    candidate_skills = load_candidate_skills()
    target_roles = load_target_roles()
    candidate_experience = load_candidate_experience()
    candidate_projects = load_candidate_projects()

    

    connection = get_connection()
    cursor = connection.cursor()
    
    if not job_ids:
        print("No new jobs to evaluate.")
        return


    placeholders = ", ".join(["%s"] * len(job_ids))

    cursor.execute(
        f"""
        SELECT
            id,
            title,
            company,
            location,
            skills,
            experience_required,
            description,
            application_url
        FROM jobs
        WHERE id IN ({placeholders})
        ORDER BY id;
        """,
        job_ids
    )

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
        experience_required,
        description,
        application_url
    ) in jobs:

        job_skills = job_skills or []
        
        if title in ["IT Systems Engineer", "Site Engineer"]:
            print("\n" + "=" * 80)
            print(f"DEBUG JOB: {title}")
            print("=" * 80)
            print("\nEXTRACTED SKILLS:")
            print(job_skills)
            print("\nFULL JOB DESCRIPTION:")
            print(description)
            print("=" * 80)

        
        eligibility = classify_eligibility(
        title,
        experience_required or "",
        description or ""
    )

        if eligibility == "not_eligible":
            continue

        match_result = match_job(
    candidate_skills=candidate_skills,
    job_title=title,
    job_skills=job_skills,
    experience_required=experience_required or "",
    target_roles=target_roles,
    job_description=description or "",
    candidate_experience=candidate_experience,
    candidate_projects=candidate_projects
)

        results.append({
            "job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "application_url": application_url,
            "eligibility": eligibility,
            "skill_score": match_result["skill_score"],
            "role_score": match_result["role_score"],
            "experience_score": match_result["experience_score"],
            "semantic_score": match_result["semantic_score"],
            "semantic_skill_similarity": match_result["semantic_skill_similarity"],
            "semantic_experience_similarity": match_result["semantic_experience_similarity"],
            "semantic_project_similarity": match_result["semantic_project_similarity"],
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
    # Save and notify new matches above the threshold
    for job in matching_jobs:

        saved = save_match({
            "job_id": job["job_id"],
            "final_score": job["final_score"],
            "matched_skills": job["matched_skills"],
            "missing_skills": job["missing_skills"],
            "role_score": job["role_score"],
            "skill_score": job["skill_score"],
            "experience_score": job["experience_score"],
            "semantic_score": job["semantic_score"],
            "application_url": job["application_url"],
        })

        if saved:
            message = (
                "🚀 New MyJob Match!\n\n"
                f"Role: {job['title']}\n"
                f"Company: {job['company']}\n"
                f"Location: {job['location']}\n\n"
                f"Apply: {job['application_url']}\n\n"
                f"Match Score: {job['final_score']}%\n"
                f"Skill Score: {job['skill_score']}%\n"
                f"Role Score: {job['role_score']}%\n"
                f"Experience Score: {job['experience_score']}%\n"
                f"Semantic Score: {job['semantic_score']}%\n\n"
                f"Matched Skills: {', '.join(job['matched_skills']) or 'None'}\n"
                f"Missing Skills: {', '.join(job['missing_skills']) or 'None'}"
            )

            send_telegram_message(message)

            print(
                f"📱 Telegram notification sent: "
                f"{job['title']} ({job['final_score']}%)"
            )
    print("\n===== ALL ELIGIBLE/UNCERTAIN JOBS =====")

    for job in results:
        print(
        job["title"],
        "|",
        job["eligibility"],
        "|",
        job["final_score"]
    )
        
    print("\n===== TOP MATCH DETAILS =====")

    top_matches = sorted(
    results,
    key=lambda job: job["final_score"],
    reverse=True
    )
    for job in top_matches[:3]:
        print("\n" + "=" * 60)
        print(f'{job["title"]} ({job["company"]})')
        print(f'Final score: {job["final_score"]}%')
        print(f'Skill score: {job["skill_score"]}%')
        print(f'Role score: {job["role_score"]}%')
        print(f'Experience score: {job["experience_score"]}%')
        print(f'Semantic score: {job["semantic_score"]}%')
        print(f'Semantic skill similarity: {job["semantic_skill_similarity"]}%')
        print(f'Semantic experience similarity: {job["semantic_experience_similarity"]}%')
        print(f'Semantic project similarity: {job["semantic_project_similarity"]}%')
        print(f'Matched skills: {job["matched_skills"]}')
        print(f'Missing skills: {job["missing_skills"]}')
        print(f'Eligibility: {job["eligibility"]}')
    
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
    print("Please provide job IDs when calling evaluate_jobs().")