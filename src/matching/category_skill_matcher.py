from src.matching.skill_categorizer import categorize_skills


def compare_skills_by_category(
    candidate_skills: list[str],
    job_skills: list[str]
) -> dict:
    """
    Compare candidate and job skills category by category.
    """

    candidate_categories = categorize_skills(
        candidate_skills
    )

    job_categories = categorize_skills(
        job_skills
    )

    results = {}

    for category in job_categories:

        candidate_set = {
            skill.lower()
            for skill in candidate_categories[category]
        }

        job_set = {
            skill.lower()
            for skill in job_categories[category]
        }

        matched = candidate_set.intersection(job_set)
        missing = job_set.difference(candidate_set)

        results[category] = {
            "matched": sorted(matched),
            "missing": sorted(missing),
            "total_required": len(job_set),
        }

    return results