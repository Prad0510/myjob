from src.matching.category_skill_matcher import (
    compare_skills_by_category
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
        "FastAPI",
        "PostgreSQL",
        "AWS",
        "Git",
    ]

    results = compare_skills_by_category(
        candidate_skills,
        job_skills
    )

    print("\n===== CATEGORY SKILL MATCH =====")

    for category, result in results.items():

        if result["total_required"] == 0:
            continue

        print(f"\n{category}")

        print("Matched:", result["matched"])
        print("Missing:", result["missing"])
        print(
            "Required:",
            result["total_required"]
        )


if __name__ == "__main__":
    main()