from src.normalization.raw_job import RawJob
from src.normalization.job import Job
from src.normalization.fingerprint import generate_job_fingerprint
from src.normalization.html_cleaner import clean_html


def normalize_job(raw_job: RawJob) -> Job:

    data = raw_job.raw_data

    # Clean HTML from the job description
    description = clean_html(
        data.get("description", "")
    )

    fingerprint = generate_job_fingerprint(
        title=data.get("title", ""),
        company=data.get("company", ""),
        application_url=data.get("application_url", ""),
    )

    return Job(
        title=data.get("title", ""),
        company=data.get("company", ""),
        location=data.get("location", ""),
        description=description,
        skills=data.get("skills", []),
        experience_required=data.get(
            "experience_required", ""
        ),
        employment_type=data.get(
            "employment_type", ""
        ),
        application_method=data.get(
            "application_method", ""
        ),
        application_url=data.get(
            "application_url", ""
        ),
        source=raw_job.source,
        source_type=raw_job.source_type,
        source_job_id=data.get(
            "source_job_id", ""
        ),
        fingerprint=fingerprint,
    )