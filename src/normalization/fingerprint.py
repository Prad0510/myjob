import hashlib


def generate_job_fingerprint(
    title: str,
    company: str,
    application_url: str = "",
) -> str:
    """
    Generate a consistent fingerprint for a job.

    Used when the original source does not provide
    a unique job ID.
    """

    raw_value = "|".join([
        title.strip().lower(),
        company.strip().lower(),
        application_url.strip().lower(),
    ])

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()