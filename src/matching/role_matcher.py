import re


def calculate_role_score(
    job_title: str,
    target_roles: list[str]
) -> float:
    """
    Calculate how closely the job title matches
    the candidate's target roles.
    """

    title = job_title.lower()

    # Strong combinations
    if "python" in title and "backend" in title:
        return 100.0

    if "java" in title and (
        "developer" in title
        or "engineer" in title
    ):
        return 100.0

    if "data engineer" in title:
        return 100.0

    if (
        "software engineer" in title
        or "software developer" in title
    ):
        return 100.0

    # Exact target-role match
    for role in target_roles:

        role_lower = role.lower()

        if role_lower in title:
            return 100.0

    # Partial role matches
    role_keywords = {
        "backend": 85.0,
        "python": 80.0,
        "java": 80.0,
        "data": 75.0,
    }

    for keyword, score in role_keywords.items():

        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, title):
            return score

    return 0.0