import json
import math
from collections import Counter

import pandas as pd

from src.ml.skill_extractor import (
    extract_skills,
    extract_roles,
    extract_seniority,
)


INPUT_FILE = "data/processed/technical_jobs.csv"
OUTPUT_FILE = "data/processed/technical_job_feature_matrix.csv"
WEIGHTS_FILE = "data/processed/technical_skill_weights.json"


SKILL_GROUPS = {
    "programming": {
        "Python",
        "Java",
        "C",
        "C++",
        "C#",
        "JavaScript",
        "TypeScript",
    },
    "backend": {
        "FastAPI",
        "Flask",
        "Django",
        "Spring Boot",
        "Node.js",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
        "REST API",
        "GraphQL",
    },
    "frontend": {
        "React",
        "Angular",
        "HTML",
        "CSS",
    },
    "data": {
        "SQL",
        "Pandas",
        "NumPy",
        "Apache Spark",
        "Hadoop",
        "Kafka",
        "Airflow",
        "Data Engineering",
        "Data Science",
        "ETL",
        "ELT",
    },
    "cloud_devops": {
        "AWS",
        "Azure",
        "GCP",
        "Docker",
        "Kubernetes",
        "Linux",
        "Git",
        "GitHub",
        "CI/CD",
    },
    "machine_learning": {
        "Machine Learning",
        "Deep Learning",
        "PyTorch",
        "TensorFlow",
        "Scikit-learn",
    },
}


def calculate_idf(skill_sets):
    """
    Calculate an IDF-like weight for each skill.

    Skills appearing in many jobs receive lower weight.
    Skills appearing in fewer jobs receive higher weight.
    """

    total_documents = len(skill_sets)
    document_frequency = Counter()

    for skills in skill_sets:
        for skill in skills:
            document_frequency[skill] += 1

    weights = {}

    for skill, frequency in document_frequency.items():
        weights[skill] = math.log(
            (total_documents + 1) / (frequency + 1)
        ) + 1

    return weights


def build_features(df):
    print("\nExtracting structured features...")

    # ---------------------------------------------------------
    # Extract skills / roles / seniority
    # ---------------------------------------------------------

    df["extracted_skills"] = df.apply(
        lambda row: extract_skills(
            f"{row['title']} {row['description']}"
        ),
        axis=1,
    )

    df["extracted_roles"] = df["title"].apply(
        extract_roles
    )

    df["extracted_seniority"] = df["title"].apply(
        extract_seniority
    )

    # ---------------------------------------------------------
    # IDF weights
    # ---------------------------------------------------------

    skill_weights = calculate_idf(
        df["extracted_skills"]
    )

    # ---------------------------------------------------------
    # Role features
    # ---------------------------------------------------------

    all_roles = sorted(
        {
            role
            for roles in df["extracted_roles"]
            for role in roles
        }
    )

    for role in all_roles:
        df[f"role__{role}"] = df[
            "extracted_roles"
        ].apply(
            lambda roles: 1.0 if role in roles else 0.0
        )

    # ---------------------------------------------------------
    # Seniority features
    # ---------------------------------------------------------

    all_seniority = sorted(
        {
            level
            for levels in df["extracted_seniority"]
            for level in levels
        }
    )

    for level in all_seniority:
        df[f"seniority__{level}"] = df[
            "extracted_seniority"
        ].apply(
            lambda levels: 1.0 if level in levels else 0.0
        )

    # ---------------------------------------------------------
    # Skill features
    # ---------------------------------------------------------

    all_skills = sorted(skill_weights.keys())

    for skill in all_skills:
        df[f"skill__{skill}"] = df[
            "extracted_skills"
        ].apply(
            lambda skills: (
                skill_weights.get(skill, 1.0)
                if skill in skills
                else 0.0
            )
        )

    # ---------------------------------------------------------
    # Technical domain features
    # ---------------------------------------------------------

    for group_name, group_skills in SKILL_GROUPS.items():

        df[f"domain__{group_name}_count"] = df[
            "extracted_skills"
        ].apply(
            lambda skills: len(
                set(skills) & group_skills
            )
        )

    # ---------------------------------------------------------
    # Aggregate technical features
    # ---------------------------------------------------------

    df["technical_skill_count"] = df[
        "extracted_skills"
    ].apply(len)

    description_length = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.len()
    )

    df["technical_skill_density"] = (
        df["technical_skill_count"]
        / description_length.clip(lower=100)
    )

    df["technical_domain_count"] = df[
        [
            f"domain__{group}_count"
            for group in SKILL_GROUPS
        ]
    ].gt(0).sum(axis=1)

    # ---------------------------------------------------------
    # Remove temporary columns
    # ---------------------------------------------------------

    df = df.drop(
        columns=[
            "extracted_skills",
            "extracted_roles",
            "extracted_seniority",
        ]
    )

    return df, skill_weights


def main():

    print("=" * 60)
    print("BUILDING TECHNICAL JOB FEATURE MATRIX")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load technical jobs
    # ---------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    print(
        f"\nTechnical jobs loaded: {len(df)}"
    )

    # ---------------------------------------------------------
    # Build features
    # ---------------------------------------------------------

    df, skill_weights = build_features(df)

    # ---------------------------------------------------------
    # Identify ML features
    # ---------------------------------------------------------

    metadata_columns = {
        "id",
        "title",
        "company",
        "location",
        "description",
        "application_url",
        "technical_title",
        "technical_skill_evidence",
        "is_technical",
    }

    feature_columns = [
        column
        for column in df.columns
        if column not in metadata_columns
    ]

    print(
        f"\nFeature matrix shape: {df.shape}"
    )

    print(
        f"ML features: {len(feature_columns)}"
    )

    print("\nDomain features:")

    for group in SKILL_GROUPS:
        print(
            f"  - domain__{group}_count"
        )

    print("\nAdditional technical features:")
    print("  - technical_skill_count")
    print("  - technical_skill_density")
    print("  - technical_domain_count")

    # ---------------------------------------------------------
    # Save feature matrix
    # ---------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    with open(
        WEIGHTS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            skill_weights,
            file,
            indent=2,
        )

    print(
        f"\nSaved: {OUTPUT_FILE}"
    )

    print(
        f"Saved: {WEIGHTS_FILE}"
    )

    print("\n" + "=" * 60)
    print("TECHNICAL FEATURE ENGINEERING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()