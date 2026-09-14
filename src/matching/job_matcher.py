from src.matching.role_compatibility import calculate_role_compatibility
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
from src.matching.semantic_matcher import (
    calculate_semantic_components
)
from src.matching.final_score import calculate_final_score


def match_job(
    candidate_skills: list[str],
    job_title: str,
    job_skills: list[str],
    experience_required: str = "",
    target_roles: list[str] | None = None,
    job_description: str = "",
    candidate_experience: str = "",
    candidate_projects: str = ""
) -> dict:

    if target_roles is None:
        target_roles = []

    # -------------------------
    # Structured matching
    # -------------------------

    skill_score = calculate_weighted_skill_score(
        candidate_skills,
        job_title,
        job_skills
    )

    role_score = calculate_role_compatibility(
        job_title,
        target_roles
    )

    experience_score = calculate_experience_score(
        experience_required,
        job_title
    )

    # -------------------------
    # Semantic matching
    # -------------------------

    semantic_result = calculate_semantic_components(
        candidate_skills=candidate_skills,
        candidate_experience=candidate_experience,
        candidate_projects=candidate_projects,
        job_skills=job_skills,
        job_description=job_description
    )

    semantic_score = semantic_result["semantic_score"]

    # -------------------------
    # Hybrid final score
    # -------------------------

    final_score = calculate_final_score(
        skill_score=skill_score,
        role_score=role_score,
        experience_score=experience_score,
        semantic_score=semantic_score
    )

    # -------------------------
    # Skill details
    # -------------------------

    category_results = compare_skills_by_category(
        candidate_skills,
        job_skills
    )

    matched_skills = []
    missing_skills = []

    for result in category_results.values():
        matched_skills.extend(result["matched"])
        missing_skills.extend(result["missing"])

    return {
        "job_title": job_title,

        "matched_skills": sorted(set(matched_skills)),
        "missing_skills": sorted(set(missing_skills)),

        "skill_score": skill_score,
        "role_score": role_score,
        "experience_score": experience_score,

        "semantic_score": semantic_score,
        "semantic_skill_similarity":
            semantic_result["skill_similarity"],
        "semantic_experience_similarity":
            semantic_result["experience_similarity"],
        "semantic_project_similarity":
            semantic_result["project_similarity"],

        "final_score": final_score,
    }