from src.matching.weighted_skill_score import (
    calculate_weighted_skill_score
)

from src.matching.category_skill_matcher import (
    compare_skills_by_category
)

from src.matching.role_matcher import calculate_role_score

from src.matching.experience_matcher import (
    calculate_experience_score
)

from src.matching.final_score import calculate_final_score


def match_job(
    candidate_skills: list[str],
    job_title: str,
    job_skills: list[str],
    experience_required: str = "",
    target_roles: list[str] | None = None,
    job_description: str = ""
) -> dict:
    
    if target_roles is None:
        target_roles = []

    skill_score = calculate_weighted_skill_score(
        candidate_skills,
        job_title,
        job_skills
    )

    role_score = calculate_role_score(
        job_title,
        target_roles
    )

    experience_score = calculate_experience_score(
        experience_required,
        job_title
    )

    final_score = calculate_final_score(
        skill_score,
        role_score,
        experience_score
    )

    # Get category-level matching details
    category_results = compare_skills_by_category(
        candidate_skills,
        job_skills
    )

    matched_skills = []
    missing_skills = []

    for result in category_results.values():

        matched_skills.extend(
            result["matched"]
        )

        missing_skills.extend(
            result["missing"]
        )

    return {
        "job_title": job_title,
        "matched_skills": sorted(set(matched_skills)),
        "missing_skills": sorted(set(missing_skills)),
        "skill_score": skill_score,
        "role_score": role_score,
        "experience_score": experience_score,
        "final_score": final_score,
    }