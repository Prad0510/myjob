from src.database.connection import get_connection


def match_exists(job_id: int, user_id: int | None = None) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if user_id is not None:
                cursor.execute(
                    """
                    SELECT 1
                    FROM job_matches
                    WHERE job_id = %s AND user_id = %s
                    """,
                    (job_id, user_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT 1
                    FROM job_matches
                    WHERE job_id = %s
                    """,
                    (job_id,),
                )
            return cursor.fetchone() is not None
    finally:
        connection.close()


def save_match(match: dict, user_id: int | None = None) -> bool:
    """Save match result for a specific user. Returns True if inserted, False if already exists."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO job_matches (
                    user_id,
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, job_id) DO NOTHING
                """,
                (
                    user_id,
                    match["job_id"],
                    match["final_score"],
                    match["matched_skills"],
                    match["missing_skills"],
                    match["role_score"],
                    match["skill_score"],
                    match["experience_score"],
                    match["semantic_score"],
                    match["application_url"],
                ),
            )
            inserted = cursor.rowcount == 1
        connection.commit()
        return inserted
    finally:
        connection.close()
