import pandas as pd

from src.database.connection import get_connection


# Roles that indicate a technical job
TECHNICAL_ROLES = {
    "backend",
    "frontend",
    "fullstack",
    "software",
    "data_engineering",
    "data_science",
    "devops",
    "cloud",
    "security",
}

# Strong technical keywords for job titles
TECHNICAL_TITLE_KEYWORDS = [
    "software engineer",
    "software developer",
    "backend engineer",
    "backend developer",
    "frontend engineer",
    "frontend developer",
    "fullstack engineer",
    "full stack engineer",
    "fullstack developer",
    "full stack developer",
    "data engineer",
    "data scientist",
    "machine learning engineer",
    "ml engineer",
    "devops engineer",
    "cloud engineer",
    "security engineer",
    "security software engineer",
    "site reliability engineer",
    "sre",
    "platform engineer",
    "analytics engineer",
    "product engineer",
    "developer",
]


def load_jobs():
    conn = get_connection()

    query = """
        SELECT
            id,
            title,
            company,
            location,
            description
        FROM jobs
        WHERE status = 'active'
        ORDER BY id;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def detect_technical_role(title):
    title = str(title).lower()

    for keyword in TECHNICAL_TITLE_KEYWORDS:
        if keyword in title:
            return True

    return False


def detect_technical_skills(title, description):
    text = f"{title} {description}".lower()

    technical_keywords = [
        "python",
        "java",
        "c++",
        "c#",
        "javascript",
        "typescript",
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "fastapi",
        "flask",
        "django",
        "spring boot",
        "react",
        "node.js",
        "angular",
        "pandas",
        "numpy",
        "scikit-learn",
        "pytorch",
        "tensorflow",
        "spark",
        "hadoop",
        "kafka",
        "airflow",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "graphql",
        "rest api",
        "machine learning",
        "deep learning",
        "data engineering",
        "data science",
        "etl",
        "ci/cd",
    ]

    return sum(
        1 for skill in technical_keywords
        if skill in text
    )


def classify_jobs(df):
    df["technical_title"] = df["title"].apply(
        detect_technical_role
    )

    df["technical_skill_evidence"] = df.apply(
        lambda row: detect_technical_skills(
            row["title"],
            row["description"]
        ),
        axis=1
    )

    # A job enters the technical ML dataset if:
    # 1. Its title clearly indicates a technical role
    # 2. It contains at least one technical skill
    df["is_technical"] = (
        df["technical_title"]
        & (df["technical_skill_evidence"] >= 1)
    )

    return df


def main():
    print("=" * 60)
    print("TECHNICAL JOB FILTER")
    print("=" * 60)

    df = load_jobs()

    print(f"\nActive jobs: {len(df)}")

    df = classify_jobs(df)

    technical = df[df["is_technical"]].copy()
    non_technical = df[~df["is_technical"]].copy()

    print(f"Technical jobs:     {len(technical)}")
    print(f"Non-technical jobs: {len(non_technical)}")

    print("\nTechnical jobs:")
    print("-" * 60)

    display_columns = [
        "id",
        "title",
        "company",
        "technical_skill_evidence",
    ]

    print(
        technical[display_columns]
        .to_string(index=False)
    )

    # Save the complete classification
    output_path = "data/processed/technical_job_classification.csv"

    df[
        [
            "id",
            "title",
            "company",
            "location",
            "technical_title",
            "technical_skill_evidence",
            "is_technical",
        ]
    ].to_csv(output_path, index=False)

    # Save only technical jobs
    technical.to_csv(
        "data/processed/technical_jobs.csv",
        index=False
    )

    print("\nSaved:")
    print(f"  {output_path}")
    print("  data/processed/technical_jobs.csv")

    print("\n" + "=" * 60)
    print("TECHNICAL FILTER COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()