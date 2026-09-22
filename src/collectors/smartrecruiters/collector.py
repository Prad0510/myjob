import requests
from src.normalization.raw_job import RawJob


class SmartRecruitersCollector:

    BASE_URL = (
        "https://api.smartrecruiters.com/v1/companies"
    )

    def __init__(self, company_slug: str, company_name: str):
        self.company_slug = company_slug
        self.company_name = company_name

    def fetch_jobs(self) -> list[RawJob]:

        jobs = []
        offset = 0
        limit = 100

        while True:

            url = (
                f"{self.BASE_URL}/"
                f"{self.company_slug}/postings"
            )

            response = requests.get(
                url,
                params={
                    "limit": limit,
                    "offset": offset,
                },
                timeout=30,
                headers={"User-Agent": "MyJob/1.0"},
            )

            response.raise_for_status()

            data = response.json()

            postings = data.get("content", [])

            if not postings:
                break

            for posting in postings:

                location_data = posting.get(
                    "location",
                    {}
                )

                location_parts = []

                if isinstance(location_data, dict):

                    city = location_data.get(
                        "city",
                        ""
                    )

                    region = location_data.get(
                        "region",
                        ""
                    )

                    country = location_data.get(
                        "country",
                        ""
                    )

                    location_parts = [
                        value
                        for value in [
                            city,
                            region,
                            country,
                        ]
                        if value
                    ]

                location = ", ".join(
                    location_parts
                )

                raw_job = RawJob(
                    source="SmartRecruiters",
                    source_type="ats",
                    raw_data={
                        "source_job_id": str(
                            posting.get("id", "")
                        ),
                        "title": posting.get(
                            "name",
                            ""
                        ),
                        "company": self.company_name,
                        "source_company": self.company_name,
                        "location": location,
                        "description": "",
                        "skills": [],
                        "experience_required": "",
                        "employment_type": "",
                        "application_method": (
                            "Company Website"
                        ),
                        "application_url": posting.get(
                            "ref",
                            ""
                        ),
                    },
                )

                jobs.append(raw_job)

            if len(postings) < limit:
                break

            offset += limit

        return jobs