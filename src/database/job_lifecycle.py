from src.database.connection import get_connection


def update_job_lifecycle(
    source: str,
    source_company: str,
    seen_source_job_ids: set[str],
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Get all currently active jobs for this exact source/company
        cursor.execute(
            """
            SELECT id, source_job_id, missed_runs
            FROM jobs
            WHERE source = %s
              AND source_company = %s
              AND status = 'active'
            """,
            (source, source_company),
        )

        active_jobs = cursor.fetchall()

        closed_count = 0
        missed_count = 0
        seen_count = 0

        for job_id, source_job_id, missed_runs in active_jobs:

            if source_job_id in seen_source_job_ids:
                # Job is still present
                cursor.execute(
                    """
                    UPDATE jobs
                    SET
                        missed_runs = 0,
                        status = 'active',
                        closed_at = NULL,
                        last_seen_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (job_id,),
                )

                seen_count += 1

            else:
                # Job was not returned by this successful collection
                new_missed_runs = (missed_runs or 0) + 1

                if new_missed_runs >= 2:
                    cursor.execute(
                        """
                        UPDATE jobs
                        SET
                            missed_runs = %s,
                            status = 'closed',
                            closed_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (new_missed_runs, job_id),
                    )

                    closed_count += 1

                else:
                    cursor.execute(
                        """
                        UPDATE jobs
                        SET
                            missed_runs = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (new_missed_runs, job_id),
                    )

                    missed_count += 1

        conn.commit()

        return {
            "seen": seen_count,
            "missed": missed_count,
            "closed": closed_count,
        }

    finally:
        cursor.close()
        conn.close()