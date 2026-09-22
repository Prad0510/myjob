from src.collectors.lever.collector import LeverCollector
from src.normalization.job_normalizer import normalize_job
from src.collectors.greenhouse.collector import GreenhouseCollector
from src.jobs.registry import SOURCES
from src.database.evaluate_jobs import evaluate_jobs
from src.collectors.test_collector import TestCollector
from src.database.job_repository import insert_job
from src.database.collection_repository import (
    start_collection_run,
    finish_collection_run,
)
from src.database.job_lifecycle import update_job_lifecycle


def sync_lever(company_slug: str, company_name: str):

    print(f"\n{'=' * 50}")
    print(f"Syncing Lever: {company_name}")
    print(f"{'=' * 50}")

    run_id = start_collection_run(
        source="Lever",
        source_company=company_name,
    )

    try:
        collector = LeverCollector(
            company_slug=company_slug,
            company_name=company_name,
        )

        raw_jobs = collector.fetch_jobs()

        print(f"Found {len(raw_jobs)} jobs")

        inserted_count = 0
        updated_count = 0
        new_job_ids = []

        for raw_job in raw_jobs:

            job = normalize_job(raw_job)

            job_id, inserted = insert_job(job)

            if inserted:
                inserted_count += 1
                new_job_ids.append(job_id)
            else:
                updated_count += 1

        seen_source_job_ids = {
            raw_job.raw_data.get("source_job_id")
            for raw_job in raw_jobs
            if raw_job.raw_data.get("source_job_id")
        }

        lifecycle_result = update_job_lifecycle(
            source="Lever",
            source_company=company_name,
            seen_source_job_ids=seen_source_job_ids,
        )

        finish_collection_run(
            run_id=run_id,
            jobs_found=len(raw_jobs),
            success=True,
        )
        
        if new_job_ids:
            print("\nEvaluating new jobs against candidate profile...")
            evaluate_jobs(new_job_ids)

        print("\nSync complete")
        print(f"Inserted: {inserted_count}")
        print(f"Updated: {updated_count}")
        print(f"Seen: {lifecycle_result['seen']}")
        print(f"Missed: {lifecycle_result['missed']}")
        print(f"Closed: {lifecycle_result['closed']}")
        print(f"New job IDs: {new_job_ids}")

    except Exception as e:

        finish_collection_run(
            run_id=run_id,
            jobs_found=0,
            success=False,
            error_message=str(e),
        )

        print(f"Sync failed: {e}")

        raise

def sync_greenhouse(board_token: str, company_name: str):

    print(f"\n{'=' * 50}")
    print(f"Syncing Greenhouse: {company_name}")
    print(f"{'=' * 50}")

    run_id = start_collection_run(
        source="Greenhouse",
        source_company=company_name,
    )

    try:
        collector = GreenhouseCollector(
            board_token=board_token,
        )

        raw_jobs = collector.fetch_jobs()

        print(f"Found {len(raw_jobs)} jobs")

        inserted_count = 0
        updated_count = 0
        new_job_ids = []

        for raw_job in raw_jobs:

            job = normalize_job(raw_job)

            job_id, inserted = insert_job(job)

            if inserted:
                inserted_count += 1
                new_job_ids.append(job_id)
            else:
                updated_count += 1

        seen_source_job_ids = {
            raw_job.raw_data.get("source_job_id")
            for raw_job in raw_jobs
            if raw_job.raw_data.get("source_job_id")
        }

        lifecycle_result = update_job_lifecycle(
            source="Greenhouse",
            source_company=company_name,
            seen_source_job_ids=seen_source_job_ids,
        )

        finish_collection_run(
            run_id=run_id,
            jobs_found=len(raw_jobs),
            success=True,
        )
        
        if new_job_ids:
            print("\nEvaluating new jobs against candidate profile...")
            evaluate_jobs(new_job_ids)

        print("\nSync complete")
        print(f"Inserted: {inserted_count}")
        print(f"Updated: {updated_count}")
        print(f"Seen: {lifecycle_result['seen']}")
        print(f"Missed: {lifecycle_result['missed']}")
        print(f"Closed: {lifecycle_result['closed']}")
        print(f"New job IDs: {new_job_ids}")

    except Exception as e:

        finish_collection_run(
            run_id=run_id,
            jobs_found=0,
            success=False,
            error_message=str(e),
        )

        print(f"Sync failed: {e}")

        raise


def main():

    for source in SOURCES:

        if source["source"] == "Lever":

            sync_lever(
                company_slug=source["slug"],
                company_name=source["company"],
            )

        elif source["source"] == "Greenhouse":

            sync_greenhouse(
                board_token=source["slug"],
                company_name=source["company"],
            )
            
        

if __name__ == "__main__":
    main()