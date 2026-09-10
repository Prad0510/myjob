from src.matching.experience_matcher import (
    classify_job_experience,
    calculate_experience_score
)


def main():

    test_jobs = [
        ("0-1 years", "Python Backend Intern"),
        ("", "Software Engineer"),
        ("3+ years", "Software Engineer"),
        ("", "Senior Data Engineer"),
        ("", "Staff Data Platform Engineer"),
        ("", "Marketing Manager"),
    ]

    for experience_required, job_title in test_jobs:

        level = classify_job_experience(
            experience_required,
            job_title
        )

        score = calculate_experience_score(
            experience_required,
            job_title
        )

        print(
            f"{job_title} → "
            f"Level: {level}, "
            f"Score: {score}%"
        )


if __name__ == "__main__":
    main()