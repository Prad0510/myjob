import requests

from src.normalization.raw_job import RawJob


class LeverCollector:

    BASE_URL = "https://api.lever.co/v0/postings"

    def __init__(self, company_slug: str, company_name: str):
        self.company_slug = company_slug
        self.company_name = company_name

    def fetch_jobs(self) -> list[RawJob]:
        url = f"{self.BASE_URL}/{self.company_slug}"

        response = requests.get(
            url,
            params={"mode": "json"},
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        data = response.json()

        jobs = []

        for job in data:
            categories = job.get("categories", {})

            location = categories.get("location", "")

            if not location:
                all_locations = categories.get("allLocations", [])
                if isinstance(all_locations, list):
                    location = ", ".join(all_locations)

            description = job.get("descriptionPlain", "")

            if not description:
                description = job.get("additionalPlain", "")

            employment_type = categories.get("commitment", "")

            raw_job = RawJob(
                source="Lever",
                source_type="ats",
                raw_data={
                    "source_job_id": str(job.get("id", "")),
                    "title": job.get("text", ""),
                    "company": self.company_name,
                    "source_company": self.company_name,
                    "location": location,
                    "description": description,
                    "skills": [],
                    "experience_required": "",
                    "employment_type": employment_type,
                    "application_method": "Company Website",
                    "application_url": job.get("hostedUrl", ""),
                }
            )

            jobs.append(raw_job)

        return jobs