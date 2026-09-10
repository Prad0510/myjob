from src.matching.candidate_loader import load_candidate_profile
from src.database.job_queries import get_jobs_with_skills
from src.matching.skill_matcher import compare_skills


def main():

    # Load candidate profile
    candidate = load_candidate_profile()

    candidate_skills = candidate["skills"]

    print("Candidate skills:")
    print(candidate_skills)

    # Get jobs from PostgreSQL
    jobs = get_jobs_with_skills()

    print("\nTotal jobs:", len(jobs))

    # Compare candidate with first 5 jobs
    for job in jobs[:5]:

        job_id, title, company, location, job_skills = job

        result = compare_skills(
            candidate_skills,
            job_skills or []
        )

        print("\n" + "=" * 70)

        print("Job ID:", job_id)
        print("Title:", title)
        print("Company:", company)
        print("Location:", location)

        print("\nJob skills:")
        print(job_skills)

        print("\nMatched skills:")
        print(result["matched_skills"])

        print("\nMissing skills:")
        print(result["missing_skills"])


if __name__ == "__main__":
    main()