import re


def classify_eligibility(
    job_title: str,
    experience_required: str = ""
) -> str:
    """
    Classify whether a job is suitable for an entry-level
    candidate looking for internships/fresher roles.
    """

    text = (
        (job_title or "") + " " +
        (experience_required or "")
    ).lower()

    # Clearly unsuitable senior roles
    senior_keywords = [
        "senior",
        "staff",
        "lead",
        "principal",
        "director",
        "manager",
        "head",
    ]

    if any(keyword in text for keyword in senior_keywords):
        return "not_eligible"

    # Clearly suitable entry-level roles
    entry_keywords = [
        "intern",
        "internship",
        "fresher",
        "entry level",
        "entry-level",
        "graduate",
        "new grad",
        "0-1 years",
        "0–1 years",
    ]

    if any(keyword in text for keyword in entry_keywords):
        return "eligible"

    # Explicit experience requirement
    year_match = re.search(
        r"(\d+)\+?\s*(?:years?|yrs?)",
        text
    )

    if year_match:

        years = int(year_match.group(1))

        if years <= 1:
            return "eligible"

        return "not_eligible"

    # No experience information
    return "uncertain"