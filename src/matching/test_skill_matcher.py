from src.matching.skill_matcher import compare_skills


def main():

    candidate_skills = [
        "Python",
        "Java",
        "React",
        "Flask",
        "MySQL",
        "Git",
    ]

    job_skills = [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "Git",
    ]

    result = compare_skills(
        candidate_skills,
        job_skills
    )

    print("Matched skills:")
    print(result["matched_skills"])

    print("\nMissing skills:")
    print(result["missing_skills"])

    print("\nTotal job skills:")
    print(result["total_job_skills"])


if __name__ == "__main__":
    main()