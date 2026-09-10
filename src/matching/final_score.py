def calculate_final_score(
    skill_score: float,
    role_score: float,
    experience_score: float
) -> float:
    """
    Calculate the final job match score.
    """

    final_score = (
        skill_score * 0.60
        + role_score * 0.25
        + experience_score * 0.15
    )

    return round(final_score, 2)