from src.database.connection import get_connection


def start_collection_run(source,source_company):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO collection_runs (source, source_company)
            VALUES (%s, %s)
            RETURNING id
            """,
            (source, source_company)
        )

        run_id = cursor.fetchone()[0]
        conn.commit()

        return run_id

    finally:
        cursor.close()
        conn.close()


def finish_collection_run(
    run_id,
    jobs_found,
    success=True,
    error_message=None
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE collection_runs
            SET
                finished_at = CURRENT_TIMESTAMP,
                jobs_found = %s,
                success = %s,
                error_message = %s
            WHERE id = %s
            """,
            (
                jobs_found,
                success,
                error_message,
                run_id,
            )
        )

        conn.commit()

    finally:
        cursor.close()
        conn.close()