from src.database.connection import get_connection


def inspect_job_descriptions():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            company,
            description
        FROM jobs
        WHERE id IN (9, 10, 11, 13)
        ORDER BY id;
    """)

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    for job_id, title, company, description in jobs:

        print("\n" + "=" * 80)
        print(f"JOB ID: {job_id}")
        print(f"TITLE: {title}")
        print(f"COMPANY: {company}")

        print("\nDESCRIPTION:")
        print(description[:5000])


if __name__ == "__main__":
    inspect_job_descriptions()