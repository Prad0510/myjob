from src.matching.skill_categorizer import categorize_skills
from src.matching.skill_matcher import get_related_skills


def compare_skills_by_category(
    candidate_skills: list[str],
    job_skills: list[str]
) -> dict:
    """
    Compare candidate and job skills category by category.

    Exact matches receive full credit.
    Related skills are recorded as partial matches.
    """

    candidate_categories = categorize_skills(
        candidate_skills
    )

    job_categories = categorize_skills(
        job_skills
    )

    # Flatten candidate skills so relationships
    # can work across different categories.
    candidate_all = {
        skill.lower()
        for skill in candidate_skills
    }

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

        partial_matches = []

        for job_skill in missing:

            related_skills = get_related_skills(
                job_skill
            )

            candidate_related = [
                skill
                for skill in related_skills
                if skill.lower() in candidate_all
            ]

            if candidate_related:
                partial_matches.append({
                    "job_skill": job_skill,
                    "candidate_skills": candidate_related
                })

        results[category] = {
            "matched": sorted(matched),
            "partial_matches": partial_matches,
            "missing": sorted(missing),
            "total_required": len(job_set),
        }

    return results