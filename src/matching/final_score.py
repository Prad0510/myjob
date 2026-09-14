def calculate_final_score(
    skill_score: float,
    role_score: float,
    experience_score: float,
    semantic_score: float = 0.0
) -> float:
    """
    Calculate the hybrid job match score.

    Structured matching:
        Skills       = 50%
        Role         = 30%
        Experience   = 20%

    Semantic matching = 20% of final score.
    """

    structured_score = (
        skill_score * 0.50
        + role_score * 0.30
        + experience_score * 0.20
    )

    final_score = (
        structured_score * 0.80
        + semantic_score * 0.20
    )

    return round(final_score, 2)