from src.matching.role_classifier import classify_role


def main():

    test_jobs = [
        "Python Backend Intern",
        "Software Engineer, Backend",
        "Senior Data Engineer - Finance",
        "Java Developer Intern",
        "Software Engineer",
        "Marketing Manager",
    ]

    print("\n===== ROLE CLASSIFICATION =====")

    for title in test_jobs:

        role = classify_role(title)

        print(f"{title} → {role}")


if __name__ == "__main__":
    main()