import requests
from src.normalization.raw_job import RawJob


class AshbyCollector:

    BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"

    def __init__(self, board_name: str, company_name: str):
        self.board_name = board_name
        self.company_name = company_name

    def fetch_jobs(self) -> list[RawJob]:

        url = f"{self.BASE_URL}/{self.board_name}"

        response = requests.get(
            url,
            params={
                "includeCompensation": "true"
            },
            timeout=30,
            headers={
                "User-Agent": "MyJob/1.0"
            },
        )

        response.raise_for_status()

        data = response.json()

        jobs = []

        for job in data.get("jobs", []):

            location = job.get("location", "")

            secondary_locations = job.get(
                "secondaryLocations", []
            )

            if secondary_locations:
                secondary_names = []

                for loc in secondary_locations:
                    if isinstance(loc, dict):
                        name = loc.get(
                            "location",
                            ""
                        )

                        if name:
                            secondary_names.append(
                                name
                            )

                if secondary_names:
                    if location:
                        location = (
                            location
                            + ", "
                            + ", ".join(
                                secondary_names
                            )
                        )
                    else:
                        location = ", ".join(
                            secondary_names
                        )

            raw_job = RawJob(
                source="Ashby",
                source_type="ats",
                raw_data={
                    "source_job_id": str(
                        job.get("id", "")
                    ),
                    "title": job.get(
                        "title",
                        ""
                    ),
                    "company": self.company_name,
                    "source_company": self.company_name,
                    "location": location,
                    "description": job.get(
                        "descriptionPlain",
                        ""
                    ),
                    "skills": [],
                    "experience_required": "",
                    "employment_type": "",
                    "application_method": (
                        "Company Website"
                    ),
                    "application_url": job.get(
                        "jobUrl",
                        ""
                    ),
                },
            )

            jobs.append(raw_job)

        return jobs