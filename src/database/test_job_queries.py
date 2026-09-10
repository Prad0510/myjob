from src.database.job_queries import get_jobs_with_skills


def main():

    jobs = get_jobs_with_skills()

    print("Total jobs:", len(jobs))

    for job in jobs[:5]:

        job_id, title, company, location, skills = job

        print("\n" + "=" * 60)
        print("ID:", job_id)
        print("Title:", title)
        print("Company:", company)
        print("Location:", location)
        print("Skills:", skills)


if __name__ == "__main__":
    main()