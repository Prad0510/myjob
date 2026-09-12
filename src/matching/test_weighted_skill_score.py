from src.matching.weighted_skill_score import (
    calculate_weighted_skill_score
)


def main():

    candidate_skills = [
        "Python",
        "Java",
        "React",
        "MySQL",
        "Git",
        "Azure",
    ]

    job_skills = [
        "Python",
    ]

    score = calculate_weighted_skill_score(
        candidate_skills,
        "Python Backend Intern",
        job_skills = [
    "Python",
    "FastAPI",
    "PostgreSQL",
]
    )

    print("\n===== WEIGHTED SKILL SCORE =====")
    print("Score:", score, "%")


if __name__ == "__main__":
    main()