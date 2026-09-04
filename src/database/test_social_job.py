from src.normalization.raw_job import RawJob
from src.normalization.job_normalizer import normalize_job
from src.database.job_repository import insert_job


def main():

    raw_job = RawJob(
        source="LinkedIn",
        source_type="social_hiring",

        raw_data={
            "title": "Python Backend Intern",
            "company": "Social Tech Company",
            "location": "Mumbai",

            "description": (
                "We are hiring a Python backend intern. "
                "DM your resume to apply."
            ),

            "skills": [
                "Python",
                "FastAPI",
            ],

            "experience_required": "0-1 years",
            "employment_type": "Internship",

            "application_method": "DM",
            "application_url": "",
        }
    )

    job = normalize_job(raw_job)

    print("Generated fingerprint:")
    print(job.fingerprint)

    job_id = insert_job(job)

    if job_id:
        print("\nJob inserted successfully!")
        print("Database ID:", job_id)


if __name__ == "__main__":
    main()