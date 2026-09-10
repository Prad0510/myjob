from src.database.connection import get_connection


def get_jobs_with_skills():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            company,
            location,
            skills
        FROM jobs
        WHERE skills IS NOT NULL;
    """)

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return jobs