from src.matching.job_matcher import match_job
from src.matching.category_skill_matcher import compare_skills_by_category


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
    
    category_results = compare_skills_by_category(
    candidate_skills,
    job_skills
)

    print("\n===== CATEGORY RESULTS =====")

    for category, result in category_results.items():
        print(f"\n{category}:")
        print("Matched:", result["matched"])
        print("Partial:", result["partial_matches"])
        print("Missing:", result["missing"])



if __name__ == "__main__":
    main()