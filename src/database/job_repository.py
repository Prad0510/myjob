from src.database.connection import get_connection
from src.normalization.job import Job


def job_exists(job: Job) -> bool:

    connection = get_connection()
    cursor = connection.cursor()

    # If the source provides an ID, use it.
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

    # Otherwise use the fingerprint.
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

    cursor.close()
    connection.close()

    return result is not None


def insert_job(job: Job):

    if job_exists(job):
        print("Job already exists. Skipping insertion.")
        return None

    connection = get_connection()
    cursor = connection.cursor()

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
            fingerprint
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
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
        ),
    )

    job_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return job_id