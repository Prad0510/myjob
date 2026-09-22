import time
from datetime import datetime

from src.jobs.sync import main


def run_scheduler():

    print("MyJob scheduler started.")

    while True:

        print(
            f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            "Starting job sync..."
        )

        try:
            main()
            print("Job sync completed successfully.")

        except Exception as e:
            print(f"Job sync failed: {e}")

        print("Next sync in 6 hours.")

        time.sleep(6 * 60 * 60)


if __name__ == "__main__":
    run_scheduler()