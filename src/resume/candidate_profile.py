from dataclasses import asdict, dataclass, field
from typing import List


@dataclass
class Education:
    degree: str
    institution: str
    start_year: str = ""
    end_year: str = ""


@dataclass
class Experience:
    role: str
    organization: str = ""
    duration: str = ""
    description: str = ""


@dataclass
class Project:
    name: str
    technologies: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class CandidateProfile:
    name: str = ""
    skills: List[str] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    target_roles: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)