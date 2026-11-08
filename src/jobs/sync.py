from src.collectors.lever.collector import LeverCollector
from src.normalization.job_normalizer import normalize_job
from src.collectors.greenhouse.collector import GreenhouseCollector
from src.jobs.registry import SOURCES
from src.database.evaluate_jobs import evaluate_jobs
from src.collectors.ashby.collector import AshbyCollector
from src.collectors.smartrecruiters.collector import SmartRecruitersCollector
from src.database.job_repository import insert_job
from src.database.collection_repository import (
    start_collection_run,
    finish_collection_run,
)
from src.database.job_lifecycle import update_job_lifecycle
from src.utils.logger import get_logger

logger = get_logger("sync")


def sync_lever(company_slug: str, company_name: str):
    logger.info(f"Syncing Lever: {company_name} (slug: {company_slug})")

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
        logger.info(f"Lever [{company_name}]: Found {len(raw_jobs)} jobs")

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
            logger.info(f"Evaluating {len(new_job_ids)} new jobs against candidate profile...")
            evaluate_jobs(new_job_ids)

        logger.info(
            f"Lever [{company_name}] sync complete: "
            f"Inserted={inserted_count}, Updated={updated_count}, "
            f"Seen={lifecycle_result['seen']}, Missed={lifecycle_result['missed']}, "
            f"Closed={lifecycle_result['closed']}"
        )

    except Exception as e:
        finish_collection_run(
            run_id=run_id,
            jobs_found=0,
            success=False,
            error_message=str(e),
        )
        logger.error(f"Lever [{company_name}] sync failed: {e}", exc_info=True)
        raise


def sync_greenhouse(board_token: str, company_name: str):
    logger.info(f"Syncing Greenhouse: {company_name} (token: {board_token})")

    run_id = start_collection_run(
        source="Greenhouse",
        source_company=company_name,
    )

    try:
        collector = GreenhouseCollector(
            board_token=board_token,
        )

        raw_jobs = collector.fetch_jobs()
        logger.info(f"Greenhouse [{company_name}]: Found {len(raw_jobs)} jobs")

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
            logger.info(f"Evaluating {len(new_job_ids)} new jobs against candidate profile...")
            evaluate_jobs(new_job_ids)

        logger.info(
            f"Greenhouse [{company_name}] sync complete: "
            f"Inserted={inserted_count}, Updated={updated_count}, "
            f"Seen={lifecycle_result['seen']}, Missed={lifecycle_result['missed']}, "
            f"Closed={lifecycle_result['closed']}"
        )

    except Exception as e:
        finish_collection_run(
            run_id=run_id,
            jobs_found=0,
            success=False,
            error_message=str(e),
        )
        logger.error(f"Greenhouse [{company_name}] sync failed: {e}", exc_info=True)
        raise


def sync_ashby(
    board_name: str,
    company_name: str,
):
    logger.info(f"Syncing Ashby: {company_name} (board: {board_name})")

    run_id = start_collection_run(
        source="Ashby",
        source_company=company_name,
    )

    try:
        collector = AshbyCollector(
            board_name=board_name,
            company_name=company_name,
        )

        raw_jobs = collector.fetch_jobs()
        logger.info(f"Ashby [{company_name}]: Found {len(raw_jobs)} jobs")

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
            source="Ashby",
            source_company=company_name,
            seen_source_job_ids=seen_source_job_ids,
        )

        finish_collection_run(
            run_id=run_id,
            jobs_found=len(raw_jobs),
            success=True,
        )

        if new_job_ids:
            logger.info(f"Evaluating {len(new_job_ids)} new jobs against candidate profile...")
            evaluate_jobs(new_job_ids)

        logger.info(
            f"Ashby [{company_name}] sync complete: "
            f"Inserted={inserted_count}, Updated={updated_count}, "
            f"Seen={lifecycle_result['seen']}, Missed={lifecycle_result['missed']}, "
            f"Closed={lifecycle_result['closed']}"
        )

    except Exception as e:
        finish_collection_run(
            run_id=run_id,
            jobs_found=0,
            success=False,
            error_message=str(e),
        )
        logger.error(f"Ashby [{company_name}] sync failed: {e}", exc_info=True)
        raise


def sync_smartrecruiters(
    company_slug: str,
    company_name: str,
):
    logger.info(f"Syncing SmartRecruiters: {company_name} (slug: {company_slug})")

    run_id = start_collection_run(
        source="SmartRecruiters",
        source_company=company_name,
    )

    try:
        collector = SmartRecruitersCollector(
            company_slug=company_slug,
            company_name=company_name,
        )

        raw_jobs = collector.fetch_jobs()
        logger.info(f"SmartRecruiters [{company_name}]: Found {len(raw_jobs)} jobs")

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
            source="SmartRecruiters",
            source_company=company_name,
            seen_source_job_ids=seen_source_job_ids,
        )

        finish_collection_run(
            run_id=run_id,
            jobs_found=len(raw_jobs),
            success=True,
        )

        if new_job_ids:
            logger.info(f"Evaluating {len(new_job_ids)} new jobs against candidate profile...")
            evaluate_jobs(new_job_ids)

        logger.info(
            f"SmartRecruiters [{company_name}] sync complete: "
            f"Inserted={inserted_count}, Updated={updated_count}, "
            f"Seen={lifecycle_result['seen']}, Missed={lifecycle_result['missed']}, "
            f"Closed={lifecycle_result['closed']}"
        )

    except Exception as e:
        finish_collection_run(
            run_id=run_id,
            jobs_found=0,
            success=False,
            error_message=str(e),
        )
        logger.error(f"SmartRecruiters [{company_name}] sync failed: {e}", exc_info=True)
        raise


def main():
    logger.info("Starting collection runs across all registered sources...")
    for source in SOURCES:
        try:
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
            elif source["source"] == "Ashby":
                sync_ashby(
                    board_name=source["slug"],
                    company_name=source["company"],
                )
            elif source["source"] == "SmartRecruiters":
                sync_smartrecruiters(
                    company_slug=source["slug"],
                    company_name=source["company"],
                )
        except Exception as e:
            # Log error for this specific source and continue to other sources so one failure doesn't abort the entire sync
            logger.error(f"Error syncing {source['source']} ({source['company']}): {e}")
            continue

    logger.info("All collection runs completed.")


if __name__ == "__main__":
    main()
