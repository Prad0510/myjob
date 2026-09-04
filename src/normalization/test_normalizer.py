from src.normalization.raw_job import RawJob
from src.normalization.job_normalizer import normalize_job


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

        }
    )

    job = normalize_job(raw_job)

    print("\n========== NORMALIZED JOB ==========")

    print("Title:", job.title)
    print("Company:", job.company)
    print("Location:", job.location)
    print("Description:", job.description)
    print("Skills:", job.skills)
    print("Experience:", job.experience_required)
    print("Employment Type:", job.employment_type)
    print("Application Method:", job.application_method)
    print("Source:", job.source)
    print("Source Type:", job.source_type)


if __name__ == "__main__":
    main()