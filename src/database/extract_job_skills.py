from src.database.connection import get_connection
from src.matching.skill_extractor import extract_skills


def extract_job_skills():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, description
        FROM jobs
        WHERE description IS NOT NULL
        ORDER BY id
        LIMIT 10;
    """)

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    for job_id, title, description in jobs:

        skills = extract_skills(description)

        print("\n" + "=" * 60)
        print(f"Job ID: {job_id}")
        print(f"Title: {title}")
        print(f"Skills: {skills}")


if __name__ == "__main__":
    extract_job_skills()