from src.matching.category_skill_matcher import (
    compare_skills_by_category
)

from src.matching.role_classifier import classify_role

from src.matching.skill_weights import (
    ROLE_SKILL_WEIGHTS
)


def calculate_weighted_skill_score(
    candidate_skills: list[str],
    job_title: str,
    job_skills: list[str]
) -> float:
    """
    Calculate a role-dependent weighted skill score.
    """

    role = classify_role(job_title)

    weights = ROLE_SKILL_WEIGHTS.get(
        role,
        ROLE_SKILL_WEIGHTS["default"]
    )

    category_results = compare_skills_by_category(
        candidate_skills,
        job_skills
    )

    total_score = 0.0

    for category, weight in weights.items():

        result = category_results.get(
            category,
            {
                "matched": [],
                "missing": [],
                "total_required": 0
            }
        )

        total_required = result["total_required"]

        if total_required == 0:
            continue

        matched = len(result["matched"])

        category_score = (
            matched / total_required
        ) * 100

        total_score += (
            category_score * weight / 100
        )

    return round(total_score, 2)