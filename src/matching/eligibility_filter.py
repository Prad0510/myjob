import re


def classify_eligibility(
    job_title: str,
    experience_required: str = "",
    description: str = ""
) -> str:
    """
    Classify whether a job is suitable for an entry-level
    candidate looking for internships/fresher roles.

    Returns:
        "eligible"      -> clearly suitable for entry-level
        "not_eligible"  -> clearly requires more experience
        "uncertain"     -> not enough information
    """

    title_text = (job_title or "").lower()
    experience_text = (experience_required or "").lower()
    description_text = (description or "").lower()

    # --------------------------------------------------
    # 1. Check senior-level keywords in JOB TITLE only
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
        return "not_eligible"

    # --------------------------------------------------
    # 2. Check explicit experience requirement
    #
    # Only consider phrases that actually indicate
    # required candidate experience.
    # --------------------------------------------------

    experience_sources = [
        experience_text,
        description_text,
    ]

    experience_patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?experience",
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?relevant\s+experience",
        r"(?:minimum|at least)\s+(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?experience",
    ]

    for text in experience_sources:

        for pattern in experience_patterns:

            matches = re.findall(pattern, text)

            for match in matches:

                if isinstance(match, tuple):
                    years = [
                        int(value)
                        for value in match
                        if value
                    ]
                else:
                    years = [int(match)]

                # If the requirement contains more than
                # one year of experience, reject it.
                if any(year > 1 for year in years):
                    return "not_eligible"

                # 0 or 1 year is acceptable.
                if all(year <= 1 for year in years):
                    return "eligible"

    # --------------------------------------------------
    # 3. Check entry-level indicators
    #
    # These are checked after explicit experience
    # requirements so that a contradictory description
    # does not incorrectly make a job eligible.
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
        return "eligible"

    # Also check description for explicit entry-level
    # phrases, but not generic words like "graduate".
    entry_description_patterns = [
        r"\bopen to freshers\b",
        r"\bfor freshers\b",
        r"\bentry[- ]level\b",
        r"\bnew graduates?\b",
        r"\brecent graduates?\b",
        r"\bgraduate program\b",
        r"\bgraduate role\b",
        r"\bgraduate position\b",
        r"\b0\s*-\s*1\s*years?\b",
        r"\b0\s*to\s*1\s*years?\b",
    ]

    if any(
        re.search(
            pattern,
            description_text
        )
        for pattern in entry_description_patterns
    ):
        return "eligible"

    # --------------------------------------------------
    # 4. No clear eligibility information
    # --------------------------------------------------

    return "uncertain"
