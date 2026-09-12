from src.matching.skill_relationships import (
    SKILL_RELATIONSHIPS
)


def get_related_skills(skill: str) -> list[str]:
    """
    Return skills that are related to the given skill.
    """

    related = []

    for parent, children in SKILL_RELATIONSHIPS.items():

        if skill.lower() == parent.lower():
            related.extend(children)

        if skill.lower() in [
            child.lower()
            for child in children
        ]:
            related.append(parent)

    return related


def compare_skills(
    candidate_skills: list[str],
    job_skills: list[str]
) -> dict:
    """
    Compare candidate skills with job skills.

    Exact matches receive full credit.
    Related skills can receive partial credit.
    """

    candidate_set = {
        skill.lower()
        for skill in candidate_skills
    }

    job_set = {
        skill.lower()
        for skill in job_skills
    }

    matched = []
    partial_matches = []
    missing = []

    for job_skill in job_set:

        # Exact match
        if job_skill in candidate_set:
            matched.append(job_skill)
            continue

        # Check related skills
        related_skills = get_related_skills(job_skill)

        candidate_related = [
            skill
            for skill in related_skills
            if skill.lower() in candidate_set
        ]

        if candidate_related:
            partial_matches.append({
                "job_skill": job_skill,
                "candidate_skills": candidate_related
            })
        else:
            missing.append(job_skill)

    return {
        "matched_skills": sorted(matched),
        "partial_matches": partial_matches,
        "missing_skills": sorted(missing),
        "total_job_skills": len(job_set),
    }