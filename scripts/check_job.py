from src.database.connection import get_connection


connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT
        title,
        experience_required,
        description
    FROM jobs
    WHERE title = 'IT Systems Engineer';
""")

job = cursor.fetchone()

if job:
    print("\nTITLE:")
    print(job[0])

    print("\nEXPERIENCE:")
    print(job[1])

    print("\nDESCRIPTION:")
    print(job[2])
else:
    print("Job not found.")

cursor.close()
connection.close()