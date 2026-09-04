from src.database.connection import get_connection


def create_jobs_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (

            id SERIAL PRIMARY KEY,

            source_job_id TEXT,

            title TEXT NOT NULL,

            company TEXT,

            location TEXT,

            description TEXT,

            skills TEXT[],

            experience_required TEXT,

            employment_type TEXT,

            application_method TEXT,

            application_url TEXT,

            source TEXT,

            source_type TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("Jobs table created successfully.")


if __name__ == "__main__":
    create_jobs_table()