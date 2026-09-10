from src.database.connection import get_connection


def inspect_jobs():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            company,
            location,
            description
        FROM jobs
        WHERE description IS NOT NULL
        ORDER BY id
        LIMIT 5;
    """)

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    for job_id, title, company, location, description in jobs:

        print("\n" + "=" * 70)

        print(f"ID: {job_id}")
        print(f"Title: {title}")
        print(f"Company: {company}")
        print(f"Location: {location}")

        print("\nDescription:")
        print(description[:2000])


if __name__ == "__main__":
    inspect_jobs()