from src.normalization.raw_job import RawJob
from src.normalization.job_normalizer import normalize_job
from src.database.job_repository import insert_job


def main():

    raw_job = RawJob(
        source="LinkedIn",
        source_type="social_hiring",

        raw_data={
            "title": "Python Backend Intern",
            "company": "ABC Technologies",
            "location": "Mumbai",

            "description": (
                "Looking for a Python backend intern "
                "with experience in FastAPI and PostgreSQL."
            ),

            "skills": [
                "Python",
                "FastAPI",
                "PostgreSQL",
            ],

            "experience_required": "0-1 years",
            "employment_type": "Internship",

            "application_method": "DM",
            "application_url": "",
            "source_job_id": "linkedin-demo-001",
        }
    )

    # RawJob → Job
    job = normalize_job(raw_job)

    # Job → PostgreSQL
    job_id = insert_job(job)

    print("\nJob inserted successfully!")
    print("Database ID:", job_id)


if __name__ == "__main__":
    main()