from src.database.connection import get_connection


def match_exists(job_id: int) -> bool:
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM job_matches
                WHERE job_id = %s
                """,
                (job_id,)
            )

            return cursor.fetchone() is not None

    finally:
        connection.close()


def save_match(match: dict) -> bool:
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO job_matches (
                    job_id,
                    match_score,
                    matched_skills,
                    missing_skills,
                    role_score,
                    skill_score,
                    experience_score,
                    semantic_score,
                    application_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO NOTHING
                """,
                (
                    match["job_id"],
                    match["final_score"],
                    match["matched_skills"],
                    match["missing_skills"],
                    match["role_score"],
                    match["skill_score"],
                    match["experience_score"],
                    match["semantic_score"],
                )
            )

            inserted = cursor.rowcount == 1

        connection.commit()

        return inserted

    finally:
        connection.close()