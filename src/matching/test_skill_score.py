from src.matching.skill_score import calculate_skill_score


def main():

    matched_skills = [
        "python",
        "react",
        "git"
    ]

    total_job_skills = 5

    score = calculate_skill_score(
        matched_skills,
        total_job_skills
    )

    print("Matched skills:", matched_skills)
    print("Total job skills:", total_job_skills)
    print("Skill match score:", score, "%")


if __name__ == "__main__":
    main()