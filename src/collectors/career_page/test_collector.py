from src.collectors.career_page.collector import CareerPageCollector


collector = CareerPageCollector(
    careers_url="https://adengage.digital/careers-award-winning-company/",
    company="AdEngage"
)

jobs = collector.fetch_jobs()

print(f"Found {len(jobs)} jobs\n")

for job in jobs:
    data = job.raw_data

    print("=" * 60)
    print("Title:", data["title"])
    print("Company:", data["company"])
    print("Location:", data["location"])
    print("Employment Type:", data["employment_type"])
    print("Application URL:", data["application_url"])

    print("\nDescription:")
    print(data["description"][:300])