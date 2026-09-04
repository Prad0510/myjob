from src.normalization.job import Job


def main():

    job = Job(
        title="Python Backend Intern",
        company="ABC Technologies",
        location="Mumbai",

        description=(
            "Looking for a Python backend intern with "
            "experience in FastAPI and PostgreSQL."
        ),

        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],

        experience_required="0-1 years",
        employment_type="Internship",

        application_method="Company Website",
        application_url="https://example.com/apply",

        source="Company Website",
        source_type="formal_job",
    )

    print("\n========== JOB ==========")
    print("Title:", job.title)
    print("Company:", job.company)
    print("Location:", job.location)
    print("Description:", job.description)
    print("Skills:", job.skills)
    print("Experience:", job.experience_required)
    print("Employment Type:", job.employment_type)
    print("Application Method:", job.application_method)
    print("Application URL:", job.application_url)
    print("Source:", job.source)
    print("Source Type:", job.source_type)


if __name__ == "__main__":
    main()

