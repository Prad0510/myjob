from src.normalization.raw_job import RawJob
from src.normalization.job import Job
from src.normalization.fingerprint import generate_job_fingerprint

def normalize_job(raw_job: RawJob) -> Job:
    """
    Convert a RawJob into our standard Job format.
    """

    data = raw_job.raw_data

    return Job(
        title=data.get("title", ""),
        company=data.get("company", ""),
        location=data.get("location", ""),

        description=data.get("description", ""),

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
        fingerprint=generate_job_fingerprint(
            title=data.get("title", ""),
            company=data.get("company", ""),
            application_url=data.get("application_url", ""),
        ),
    )