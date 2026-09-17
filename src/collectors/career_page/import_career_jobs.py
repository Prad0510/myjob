from src.collectors.career_page.collector import CareerPageCollector
from src.normalization.job_normalizer import normalize_job
from src.database.job_repository import insert_job


collector = CareerPageCollector(
    careers_url="https://adengage.digital/careers-award-winning-company/",
    company="AdEngage"
)

raw_jobs = collector.fetch_jobs()

print(f"Found {len(raw_jobs)} career-page jobs\n")

inserted_count = 0
skipped_count = 0

for raw_job in raw_jobs:

    job = normalize_job(raw_job)

    inserted = insert_job(job)

    if inserted:
        inserted_count += 1
        print(f"✓ Inserted: {job.title}")
    else:
        skipped_count += 1
        print(f"↻ Skipped duplicate: {job.title}")

print("\nImport complete")
print(f"Inserted: {inserted_count}")
print(f"Skipped: {skipped_count}")