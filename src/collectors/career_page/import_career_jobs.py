from src.collectors.career_page.collector import CareerPageCollector
from src.normalization.job_normalizer import normalize_job
from src.database.job_repository import insert_job
from src.database.job_lifecycle import update_job_lifecycle

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

seen_source_job_ids = {
    raw_job.raw_data.get("source_job_id")
    for raw_job in raw_jobs
    if raw_job.raw_data.get("source_job_id")
}

lifecycle_result = update_job_lifecycle(
    source="Lever",
    source_company="Aleph",
    seen_source_job_ids=seen_source_job_ids,
)

print("\nLifecycle update")
print(f"Seen: {lifecycle_result['seen']}")
print(f"Missed: {lifecycle_result['missed']}")
print(f"Closed: {lifecycle_result['closed']}")