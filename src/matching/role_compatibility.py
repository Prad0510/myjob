import re


ROLE_GROUPS = {
    "backend": [
        "backend developer",
        "backend engineer",
        "python developer",
        "python engineer",
        "java developer",
        "java engineer",
        "api developer",
        "api engineer",
    ],

    "software": [
        "software engineer",
        "software developer",
        "software development engineer",
        "sde",
    ],

    "data": [
        "data engineer",
        "data developer",
        "data scientist",
        "machine learning engineer",
        "ml engineer",
    ],

    "frontend": [
        "frontend developer",
        "frontend engineer",
        "front end developer",
        "front end engineer",
        "web developer",
        "web engineer",
    ],

    "devops": [
        "devops engineer",
        "cloud engineer",
        "site reliability engineer",
        "sre",
    ],

    "security": [
        "security engineer",
        "security software engineer",
        "application security engineer",
        "cybersecurity engineer",
    ],

    "design": [
        "product designer",
        "visual designer",
        "ui designer",
        "ux designer",
        "ux/ui designer",
    ],

    "sales": [
        "sales development representative",
        "account executive",
        "sales engineer",
    ],

    "operations": [
        "operations",
        "product operations",
        "people operations",
    ],
}


def classify_job_role(job_title: str) -> str:
    """
    Classify a job title into a broad role group.
    """

    title = (job_title or "").lower().strip()

    for role_group, keywords in ROLE_GROUPS.items():
        for keyword in keywords:
            if keyword in title:
                return role_group

    return "unknown"


def calculate_role_compatibility(
    job_title: str,
    target_roles: list[str]
) -> float:
    """
    Calculate compatibility between a job title and the candidate's
    target roles.

    Returns a score from 0 to 100.
    """

    job_role = classify_job_role(job_title)

    if job_role == "unknown":
        return 30.0

    target_roles_lower = [
        role.lower().strip()
        for role in target_roles
    ]

    # Direct target-role match
    for target_role in target_roles_lower:
        if target_role in (job_title or "").lower():
            return 100.0

    # Determine the broad groups represented by target roles
    target_groups = set()

    for target_role in target_roles_lower:

        if "backend" in target_role:
            target_groups.add("backend")

        elif "data engineer" in target_role:
            target_groups.add("data")

        elif "software engineer" in target_role:
            target_groups.add("software")

        elif "java" in target_role:
            target_groups.add("backend")

        elif "python" in target_role:
            target_groups.add("backend")

    # Same broad role family
    if job_role in target_groups:
        return 90.0

    # Software and backend overlap
    if (
        job_role == "software"
        and "backend" in target_groups
    ):
        return 80.0

    if (
        job_role == "backend"
        and "software" in target_groups
    ):
        return 80.0

    # Other technical roles
    if job_role in {
        "frontend",
        "devops",
        "security",
        "data",
    }:
        return 0.0

    # Non-target roles
    return 0.0