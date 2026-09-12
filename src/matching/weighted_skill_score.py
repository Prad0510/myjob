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

    Exact matches receive full credit.
    Related skills receive 50% credit.

    Only categories that contain job-required skills
    contribute to the final skill score.
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

    weighted_score = 0.0
    active_weight = 0.0

    for category, weight in weights.items():

        result = category_results.get(
            category,
            {
                "matched": [],
                "partial_matches": [],
                "missing": [],
                "total_required": 0
            }
        )

        total_required = result["total_required"]

        # Ignore categories that are not required by this job
        if total_required == 0:
            continue

        exact_matches = len(
            result["matched"]
        )

        partial_matches = len(
            result["partial_matches"]
        )

        # Exact = 100% credit
        # Partial = 50% credit
        effective_matches = (
            exact_matches
            + (partial_matches * 0.5)
        )

        category_score = (
            effective_matches / total_required
        ) * 100

        # Never allow more than 100%
        category_score = min(
            category_score,
            100
        )

        weighted_score += (
            category_score * weight
        )

        active_weight += weight

    if active_weight == 0:
        return 0.0

    final_score = (
        weighted_score / active_weight
    )

    return round(final_score, 2)