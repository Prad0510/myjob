from src.normalization.raw_job import RawJob
from src.normalization.job_normalizer import normalize_job


def test_normalize_job():
    raw_job = RawJob(
        source="Greenhouse",
        source_type="formal_job",
        raw_data={
            "source_job_id": "12345",
            "title": "Senior Python Developer",
            "company": "TestCorp",
            "location": "Remote",
            "description": "<p>We are seeking a <b>Python</b> engineer with SQL experience.</p>",
            "skills": ["Python", "SQL"],
            "experience_required": "3-5 years",
            "employment_type": "Full-time",
            "application_method": "Website",
            "application_url": "https://example.com/apply/12345",
        },
    )

    job = normalize_job(raw_job)

    assert job.source_job_id == "12345"
    assert job.title == "Senior Python Developer"
    assert job.company == "TestCorp"
    assert job.location == "Remote"
    assert "Python" in job.description
    assert "SQL experience" in job.description
    assert "<p>" not in job.description
    assert "<b>" not in job.description
    assert job.fingerprint is not None and len(job.fingerprint) > 0
