from src.collectors.greenhouse.collector import GreenhouseCollector


def main():

    collector = GreenhouseCollector("vercel")

    jobs = collector.fetch_jobs()

    print("Total jobs found:", len(jobs))

    if jobs:

        first_job = jobs[0]

        print("\n--- FIRST JOB ---")
        print("Source:", first_job.source)
        print("Source type:", first_job.source_type)

        print("\nRaw data:")
        for key, value in first_job.raw_data.items():

            if key == "description":
                print(
                    f"{key}: "
                    f"{str(value)[:500]}..."
                )
            else:
                print(f"{key}: {value}")


if __name__ == "__main__":
    main()