import re


def classify_job_experience(
    experience_required: str,
    job_title: str
) -> str:
    """
    Classify the expected experience level of a job.

    Returns:
        "entry"   -> internship / fresher / 0-1 years
        "mid"     -> approximately 2 years
        "senior"  -> 3+ years or senior-level title
        "unknown" -> no clear experience information
    """

    experience_text = (
        experience_required or ""
    ).lower()

    title_text = (
        job_title or ""
    ).lower()

    # --------------------------------------------------
    # 1. Senior-level indicators in JOB TITLE
    # --------------------------------------------------

    senior_title_keywords = [
        "senior",
        "staff",
        "lead",
        "principal",
        "director",
        "manager",
        "head",
    ]

    if any(
        re.search(
            r"\b" + re.escape(keyword) + r"\b",
            title_text
        )
        for keyword in senior_title_keywords
    ):
        return "senior"

    # --------------------------------------------------
    # 2. Entry-level indicators
    # --------------------------------------------------

    entry_keywords = [
        "intern",
        "internship",
        "fresher",
        "entry level",
        "entry-level",
        "new grad",
        "new graduate",
        "graduate program",
        "graduate role",
        "graduate position",
    ]

    if any(
        keyword in title_text
        for keyword in entry_keywords
    ):
        return "entry"

    if any(
        keyword in experience_text
        for keyword in entry_keywords
    ):
        return "entry"

    # --------------------------------------------------
    # 3. Explicit experience requirement
    #
    # Only match phrases that actually describe
    # required experience.
    # --------------------------------------------------

    experience_patterns = [
    r"(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:[\w-]+\s+){0,8}experience",
    r"(?:minimum|at least)\s+(\d+)\s*(?:years?|yrs?)",
    r"(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)\s+(?:[\w-]+\s+){0,8}experience",
]
    for pattern in experience_patterns:

        match = re.search(
            pattern,
            experience_text
        )

        if match:

            years = int(match.group(1))

            if years <= 1:
                return "entry"

            if years == 2:
                return "mid"

            if years >= 3:
                return "senior"

    # --------------------------------------------------
    # 4. Experience range
    #
    # Example:
    # "2-4 years of experience"
    # --------------------------------------------------

    range_match = re.search(
        r"(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?experience",
        experience_text
    )

    if range_match:

        minimum_years = int(
            range_match.group(1)
        )

        if minimum_years <= 1:
            return "entry"

        if minimum_years == 2:
            return "mid"

        return "senior"

    # --------------------------------------------------
    # 5. No clear experience information
    # --------------------------------------------------

    return "unknown"


def calculate_experience_score(
    experience_required: str,
    job_title: str,
    candidate_level: str = "entry"
) -> float:
    """
    Compare the job's expected experience level
    with the candidate's current level.

    Score:
        100 -> strong experience-level match
         50 -> uncertain / moderate match
          0 -> clearly unsuitable experience level
    """

    job_level = classify_job_experience(
        experience_required,
        job_title
    )

    # No clear experience information
    if job_level == "unknown":
        return 50.0

    # Same experience level
    if job_level == candidate_level:
        return 100.0

    # Entry-level candidate applying to a mid-level role
    if (
        job_level == "mid"
        and candidate_level == "entry"
    ):
        return 50.0

    # Entry-level candidate applying to a senior role
    if (
        job_level == "senior"
        and candidate_level == "entry"
    ):
        return 0.0

    # Default moderate score
    return 50.0
