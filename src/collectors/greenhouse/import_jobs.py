from src.collectors.greenhouse.collector import GreenhouseCollector
from src.normalization.job_normalizer import normalize_job
from src.database.job_repository import insert_job


def main():

    collector = GreenhouseCollector("vercel")

    raw_jobs = collector.fetch_jobs()

    print("Jobs collected:", len(raw_jobs))

    inserted = 0
    skipped = 0

    for raw_job in raw_jobs:

        job = normalize_job(raw_job)

        job_id = insert_job(job)

        if job_id is not None:
            inserted += 1
        else:
            skipped += 1

    print("\nImport completed.")
    print("Inserted:", inserted)
    print("Skipped:", skipped)


if __name__ == "__main__":
    main()