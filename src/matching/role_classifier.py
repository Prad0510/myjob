import re


def classify_role(job_title: str) -> str:
    """
    Identify the main role family of a job.
    """

    title = job_title.lower()

    # Backend should be checked before software
    if re.search(r"\bbackend\b", title):
        return "backend"

    if re.search(r"\bdata engineer\b", title):
        return "data"

    if re.search(r"\bjava\b", title):
        return "java"

    if (
        re.search(r"\bsoftware engineer\b", title)
        or re.search(r"\bsoftware developer\b", title)
    ):
        return "software"

    return "default"