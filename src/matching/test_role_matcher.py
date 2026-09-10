from src.matching.role_matcher import calculate_role_score


def main():

    test_jobs = [
        "Software Engineer, Backend",
        "Senior Data Engineer - Finance",
        "Python Backend Developer",
        "Commercial Account Executive",
        "Marketing Manager",
    ]

    for job_title in test_jobs:

        score = calculate_role_score(job_title)

        print(
            f"{job_title} → {score}%"
        )


if __name__ == "__main__":
    main()