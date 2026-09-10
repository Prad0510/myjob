import requests

from src.normalization.raw_job import RawJob


class GreenhouseCollector:
    """
    Collect publicly available jobs from a Greenhouse job board.
    """

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self, board_token: str):
        self.board_token = board_token

    def fetch_jobs(self) -> list[RawJob]:

        url = (
            f"{self.BASE_URL}/"
            f"{self.board_token}/jobs"
        )

        params = {
            "content": "true"
        }

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        jobs = []

        for job in data.get("jobs", []):

            raw_job = RawJob(
                source="Greenhouse",
                source_type="formal_job",
                raw_data={
                    "source_job_id": str(job.get("id", "")),

                    "title": job.get("title", ""),

                    "company": job.get(
                        "company_name",
                        ""
                    ),

                    "location": (
                        job.get("location", {})
                        .get("name", "")
                    ),

                    "description": job.get(
                        "content",
                        ""
                    ),

                    "skills": [],

                    "experience_required": "",

                    "employment_type": "",

                    "application_method": (
                        "Company Website"
                    ),

                    "application_url": job.get(
                        "absolute_url",
                        ""
                    ),
                }
            )

            jobs.append(raw_job)

        return jobs