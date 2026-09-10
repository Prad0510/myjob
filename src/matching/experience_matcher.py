import re


def classify_job_experience(experience_required: str, job_title: str) -> str:
    """
    Classify the expected experience level of a job.
    """

    text = (
        (experience_required or "") + " " +
        (job_title or "")
    ).lower()

    # Internship / entry-level indicators
    if any(keyword in text for keyword in [
        "intern",
        "internship",
        "entry level",
        "entry-level",
        "fresher",
        "graduate",
        "new grad",
        "0-1 years",
        "0–1 years",
    ]):
        return "entry"


    # Senior-level indicators
    if any(keyword in text for keyword in [
        "senior",
        "staff",
        "lead",
        "principal",
        "director",
        "manager",
        "head",
    ]):
        return "senior"


    # Explicit years of experience
    year_match = re.search(
        r"(\d+)\+?\s*(?:years?|yrs?)",
        text
    )

    if year_match:

        years = int(year_match.group(1))

        if years <= 1:
            return "entry"

        if years >= 3:
            return "senior"

        return "mid"


    return "unknown"


def calculate_experience_score(
    experience_required: str,
    job_title: str,
    candidate_level: str = "entry"
) -> float:
    """
    Compare the job's expected experience level
    with the candidate's current level.
    """

    job_level = classify_job_experience(
        experience_required,
        job_title
    )

    if job_level == "unknown":
        return 50.0

    if job_level == candidate_level:
        return 100.0

    if job_level == "mid" and candidate_level == "entry":
        return 50.0

    if job_level == "senior" and candidate_level == "entry":
        return 0.0

    return 50.0