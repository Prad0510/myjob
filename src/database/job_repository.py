from src.database.connection import get_connection
from src.normalization.job import Job


def job_exists(job: Job) -> bool:

    connection = get_connection()
    cursor = connection.cursor()

    try:
        if job.source_job_id:
            cursor.execute(
                """
                SELECT 1
                FROM jobs
                WHERE source = %s
                  AND source_job_id = %s
                LIMIT 1;
                """,
                (
                    job.source,
                    job.source_job_id,
                ),
            )
        else:
            cursor.execute(
                """
                SELECT 1
                FROM jobs
                WHERE fingerprint = %s
                LIMIT 1;
                """,
                (job.fingerprint,),
            )

        result = cursor.fetchone()
        return result is not None

    finally:
        cursor.close()
        connection.close()


def insert_job(job: Job):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # --------------------------------------------------
        # Check whether job already exists
        # --------------------------------------------------

        if job.source_job_id:

            cursor.execute(
                """
                SELECT id
                FROM jobs
                WHERE source = %s
                  AND source_job_id = %s
                LIMIT 1;
                """,
                (
                    job.source,
                    job.source_job_id,
                ),
            )

        else:

            cursor.execute(
                """
                SELECT id
                FROM jobs
                WHERE fingerprint = %s
                LIMIT 1;
                """,
                (job.fingerprint,),
            )

        existing_job = cursor.fetchone()

        # --------------------------------------------------
        # Existing job → UPDATE
        # --------------------------------------------------

        if existing_job:

            job_id = existing_job[0]

            cursor.execute(
                """
                UPDATE jobs
                SET
                    title = %s,
                    company = %s,
                    location = %s,
                    description = %s,
                    skills = %s,
                    experience_required = %s,
                    employment_type = %s,
                    application_method = %s,
                    application_url = %s,
                    fingerprint = %s,
                    source_company = %s,
                    status = 'active',
                    missed_runs = 0,
                    last_seen_at = CURRENT_TIMESTAMP,
                    closed_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (
                    job.title,
                    job.company,
                    job.location,
                    job.description,
                    job.skills,
                    job.experience_required,
                    job.employment_type,
                    job.application_method,
                    job.application_url,
                    job.fingerprint,
                    job.source_company,
                    job_id,
                ),
            )

            connection.commit()


            return job_id, False

        # --------------------------------------------------
        # New job → INSERT
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO jobs (
                source_job_id,
                title,
                company,
                location,
                description,
                skills,
                experience_required,
                employment_type,
                application_method,
                application_url,
                source,
                source_type,
                fingerprint,
                source_company
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id;
            """,
            (
                job.source_job_id,
                job.title,
                job.company,
                job.location,
                job.description,
                job.skills,
                job.experience_required,
                job.employment_type,
                job.application_method,
                job.application_url,
                job.source,
                job.source_type,
                job.fingerprint,
                job.source_company,
            ),
        )
        job_id = cursor.fetchone()[0]

        connection.commit()

        return job_id,True

    finally:
        cursor.close()
        connection.close()