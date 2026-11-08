import os
import time
from dotenv import load_dotenv
from src.jobs.sync import main
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("scheduler")

SYNC_INTERVAL_HOURS = float(os.getenv("SYNC_INTERVAL_HOURS", 6))


def run_scheduler():
    logger.info("MyJob scheduler started.")
    logger.info(f"Sync interval set to {SYNC_INTERVAL_HOURS} hours.")

    while True:
        logger.info("Starting job sync cycle...")

        try:
            main()
            logger.info("Job sync completed successfully.")
        except Exception as e:
            logger.error(f"Job sync cycle encountered an error: {e}", exc_info=True)

        sleep_seconds = int(SYNC_INTERVAL_HOURS * 3600)
        logger.info(f"Next sync in {SYNC_INTERVAL_HOURS} hours ({sleep_seconds}s). Sleeping...")

        try:
            time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user. Shutting down gracefully.")
            break


if __name__ == "__main__":
    run_scheduler()
