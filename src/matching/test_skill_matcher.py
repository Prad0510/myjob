from src.matching.skill_matcher import compare_skills


def main():

    candidate_skills = [
        "Python",
        "Git",
        "MySQL",
    ]

    job_skills = [
        "Python",
        "PostgreSQL",
        "Docker",
        "FastAPI",
        "Git",
    ]

    result = compare_skills(
        candidate_skills,
        job_skills
    )

    print("\n===== SKILL MATCH TEST =====")

    print(
        "Matched skills:",
        result["matched_skills"]
    )

    print(
        "Partial matches:",
        result["partial_matches"]
    )

    print(
        "Missing skills:",
        result["missing_skills"]
    )

    print(
        "Total job skills:",
        result["total_job_skills"]
    )


if __name__ == "__main__":
    main()