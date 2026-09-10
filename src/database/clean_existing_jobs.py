from src.database.connection import get_connection
from src.normalization.html_cleaner import clean_html


def clean_existing_jobs():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, description
        FROM jobs
        WHERE description IS NOT NULL;
    """)

    jobs = cursor.fetchall()

    print("Jobs found:", len(jobs))

    updated = 0

    for job_id, description in jobs:

        # Skip descriptions that are already plain text
        if "<" not in description or ">" not in description:
            continue

        cleaned_description = clean_html(description)

        cursor.execute(
            """
            UPDATE jobs
            SET description = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
            """,
            (
                cleaned_description,
                job_id,
            ),
        )

        updated += 1

    connection.commit()

    cursor.close()
    connection.close()

    print("Jobs cleaned:", updated)


if __name__ == "__main__":
    clean_existing_jobs()