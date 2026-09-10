import re


ROLE_PATTERNS = {
    "backend": [
        "backend",
        "backend developer",
        "backend engineer",
        "python backend",
    ],

    "software": [
        "software engineer",
        "software developer",
    ],

    "data": [
        "data engineer",
    ],

    "python": [
        "python developer",
        "python engineer",
    ],

    "java": [
        "java developer",
        "java engineer",
    ],
}


def calculate_role_score(job_title: str) -> float:
    """
    Calculate role relevance based on keywords
    present in the job title.

    Returns:
        100.0 -> strongly relevant
        0.0   -> not relevant
    """

    title = job_title.lower()

    # Strong technical role keywords
    strong_keywords = [
        "backend",
        "software engineer",
        "software developer",
        "data engineer",
        "python developer",
        "python engineer",
        "java developer",
        "java engineer",
    ]

    for keyword in strong_keywords:

        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, title):
            return 100.0

    return 0.0