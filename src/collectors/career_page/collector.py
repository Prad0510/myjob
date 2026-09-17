import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from src.normalization.raw_job import RawJob
from src.normalization.html_cleaner import clean_html

class CareerPageCollector:

    def __init__(self, careers_url: str, company: str):
        self.careers_url = careers_url
        self.company = company

    def fetch_job_links(self) -> list[str]:
        response = requests.get(
            self.careers_url,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        job_links = []

        for link in soup.find_all("a", href=True):
            href = link["href"].strip()

            if "/jobs/" not in href:
                continue

            full_url = urljoin(
                self.careers_url,
                href
            )

            if full_url not in job_links:
                job_links.append(full_url)

        return job_links

    def parse_job_page(self, job_url: str) -> RawJob | None:

        response = requests.get(
            job_url,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        job_posting = None

        for script in soup.find_all(
            "script",
            type="application/ld+json"
        ):
            try:
                data = json.loads(
                    script.string or script.get_text()
                )
            except json.JSONDecodeError:
                continue

            if isinstance(data, dict):
                if data.get("@type") == "JobPosting":
                    job_posting = data
                    break

            elif isinstance(data, list):
                for item in data:
                    if (
                        isinstance(item, dict)
                        and item.get("@type") == "JobPosting"
                    ):
                        job_posting = item
                        break

            if job_posting:
                break

        if not job_posting:
            return None

        organization = job_posting.get(
            "hiringOrganization",
            {}
        )

        job_location = job_posting.get(
            "jobLocation",
            {}
        )

        if isinstance(job_location, list):
            job_location = (
                job_location[0]
                if job_location
                else {}
            )

        address = job_location.get(
            "address",
            ""
        )

        if isinstance(address, dict):
            location = (
                address.get("addressLocality", "")
                or address.get("streetAddress", "")
            )
        else:
            location = address

        employment_type = job_posting.get(
            "employmentType",
            ""
        )

        if isinstance(employment_type, list):
            employment_type = ", ".join(
                employment_type
            )

        return RawJob(
            source=self.company,
            source_type="company_career_page",
            raw_data={
                "source_job_id": job_url,
                "title": job_posting.get(
                    "title",
                    ""
                ),
                "company": organization.get(
                    "name",
                    self.company
                ),
                "location": clean_html(location),
                "description": clean_html(job_posting.get(
                    "description",
                    "")
                ),
                "skills": [],
                "experience_required": "",
                "employment_type": employment_type,
                "application_method": "Company Website",
                "application_url": job_url,
            }
        )

    def fetch_jobs(self) -> list[RawJob]:

        job_links = self.fetch_job_links()

        jobs = []

        for job_url in job_links:

            job = self.parse_job_page(
                job_url
            )

            if job:
                jobs.append(job)

        return jobs