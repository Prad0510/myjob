from src.database.connection import get_connection
from src.matching.skill_extractor import extract_skills


def backfill_job_skills():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, description
        FROM jobs
        WHERE description IS NOT NULL;
    """)

    jobs = cursor.fetchall()

    print("Jobs found:", len(jobs))

    updated = 0

    for job_id, title, description in jobs:

        skills = extract_skills(description)

        cursor.execute(
            """
            UPDATE jobs
            SET skills = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
            """,
            (
                skills,
                job_id,
            ),
        )

        print(
            f"Job {job_id}: "
            f"{title} → {skills}"
        )

        updated += 1

    connection.commit()

    cursor.close()
    connection.close()

    print("\nBackfill completed.")
    print("Jobs updated:", updated)


if __name__ == "__main__":
    backfill_job_skills()