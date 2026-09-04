from dataclasses import dataclass, field
from typing import List


@dataclass
class Job:
    title: str = ""
    company: str = ""
    location: str = ""

    description: str = ""

    skills: List[str] = field(default_factory=list)

    experience_required: str = ""
    employment_type: str = ""

    application_method: str = ""
    application_url: str = ""

    source: str = ""
    source_type: str = ""
    
    source_job_id: str = ""
    fingerprint: str = ""
