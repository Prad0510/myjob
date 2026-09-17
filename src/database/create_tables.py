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
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_matches (

        id SERIAL PRIMARY KEY,

        job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,

        match_score DECIMAL(5,2) NOT NULL,

        matched_skills TEXT[],

        missing_skills TEXT[],

        role_score DECIMAL(5,2),

        skill_score DECIMAL(5,2),

        experience_score DECIMAL(5,2),

        semantic_score DECIMAL(5,2),

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        UNIQUE(job_id)
    );
""")

    connection.commit()

    cursor.close()
    connection.close()

    print("Jobs table created successfully.")


if __name__ == "__main__":
    create_jobs_table()