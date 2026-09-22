from src.database.job_lifecycle import update_job_lifecycle
from src.collectors.lever.collector import LeverCollector
from src.normalization.job_normalizer import normalize_job
from src.database.job_repository import insert_job
from src.database.collection_repository import (
    start_collection_run,
    finish_collection_run,
)


collector = LeverCollector(
    company_slug="aleph",
    company_name="Aleph"
)

run_id = start_collection_run(
                              source="Lever",
    source_company="Aleph"
)

try:
    raw_jobs = collector.fetch_jobs()

    print(f"Found {len(raw_jobs)} Lever jobs\n")

    inserted_count = 0
    updated_count = 0

    for raw_job in raw_jobs:
        job = normalize_job(raw_job)

        inserted = insert_job(job)

        if inserted:
            inserted_count += 1
            print(f"✓ Inserted: {job.title}")
        else:
            updated_count += 1
            print(f"↻ Updated: {job.title}")

    finish_collection_run(
        run_id=run_id,
        jobs_found=len(raw_jobs),
        success=True
    )

    print("\nImport complete")
    print(f"Inserted: {inserted_count}")
    print(f"Updated: {updated_count}")
    
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

except Exception as e:

    finish_collection_run(
        run_id=run_id,
        jobs_found=0,
        success=False,
        error_message=str(e)
    )

    raise