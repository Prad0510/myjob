from src.matching.skill_extractor import extract_skills


def main():

    description = """
    We are looking for a Python backend developer
    with experience in FastAPI and PostgreSQL.

    Experience with Docker, Git and AWS is preferred.
    Knowledge of Machine Learning is a plus.
    """

    skills = extract_skills(description)

    print("Extracted skills:")
    print(skills)


if __name__ == "__main__":
    main()