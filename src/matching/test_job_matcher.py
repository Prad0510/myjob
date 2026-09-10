from src.matching.job_matcher import match_job


def main():

    candidate_skills = [
        "Python",
        "Java",
        "JavaScript",
        "React",
        "Node.js",
        "MySQL",
        "Git",
    ]

    job_title = "Python Backend Intern"

    job_skills = [
        "Python",
        "FastAPI",
        "PostgreSQL",
    ]

    result = match_job(
        candidate_skills,
        job_title,
        job_skills,
        "0-1 years"
    )

    print("\n===== COMPLETE JOB MATCH =====")

    print("Job:", result["job_title"])
    print("Skill score:", result["skill_score"], "%")
    print("Role score:", result["role_score"], "%")
    print(
        "Experience score:",
        result["experience_score"],
        "%"
    )
    print("Final score:", result["final_score"], "%")


if __name__ == "__main__":
    main()