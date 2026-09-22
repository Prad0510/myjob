from src.normalization.job import Job
from src.database.job_repository import insert_job


test_job = Job(
    title="Python Backend Developer Intern",
    company="MyJob Test Company",
    location="Mumbai",
    description=(
        "Looking for a Python backend developer intern "
        "with Python, Flask, PostgreSQL and Git experience."
    ),
    skills=[
        "Python",
        "Flask",
        "PostgreSQL",
        "Git",
    ],
    experience_required="0-1 years",
    employment_type="Internship",
    application_method="Company Website",
    application_url="https://example.com/test-job",
    source="Test",
    source_type="test",
    source_job_id="myjob-test-001",
    source_company="MyJob Test Company",
)

job_id, inserted = insert_job(test_job)

print(f"Job ID: {job_id}")
print(f"Inserted: {inserted}")