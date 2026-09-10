def calculate_skill_score(
    matched_skills: list[str],
    total_job_skills: int
) -> float:
    """
    Calculate the percentage of job skills
    that are present in the candidate profile.
    """

    if total_job_skills == 0:
        return 0.0

    score = (
        len(matched_skills)
        / total_job_skills
    ) * 100

    return round(score, 2)