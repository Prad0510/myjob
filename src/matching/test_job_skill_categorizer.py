from src.matching.job_skill_categorizer import categorize_job_skills


def main():

    job_skills = [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "AWS",
        "Docker",
        "Git",
    ]

    categorized = categorize_job_skills(job_skills)

    print("\n===== JOB SKILL CATEGORIES =====")

    for category, skills in categorized.items():

        print(f"\n{category}:")
        print(skills)


if __name__ == "__main__":
    main()