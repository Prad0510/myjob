from src.matching.eligibility_filter import (
    classify_eligibility
)


def main():

    test_jobs = [
        ("Python Backend Intern", ""),
        ("Software Engineer", ""),
        ("Senior Data Engineer", ""),
        ("Java Developer", "0-1 years"),
        ("Software Engineer", "2-3 years"),
        ("Director, Solutions Architect", ""),
        ("Graduate Software Engineer", ""),
    ]

    print("\n===== JOB ELIGIBILITY =====")

    for title, experience in test_jobs:

        result = classify_eligibility(
            title,
            experience
        )

        print(
            f"{title} → {result}"
        )


if __name__ == "__main__":
    main()