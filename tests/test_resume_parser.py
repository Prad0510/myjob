from src.resume.candidate_profile import CandidateProfile
from src.resume.resume_parser import build_candidate_profile, parse_resume


SAMPLE_RESUME_TEXT = """
JOHN DOE
john.doe@example.com | +1 555-0199

SKILLS
Languages & Database: Python, SQL, PostgreSQL
Frameworks & Libraries: FastAPI, Django
Tools & Platforms: Docker, Git

WORK EXPERIENCE
Software Engineer
JANUARY 2023 - PRESENT
Acme Technologies
Developed scalable microservices using Python and FastAPI.
Optimized PostgreSQL query latency by 35%.

EDUCATION
2019 - 2023
State University
Bachelor of Science in Computer Science

PROJECTS
Job Matching Engine
Tech stack: Python, PostgreSQL, Docker
Built an automated matching engine with semantic scoring.
"""


def test_parse_resume():
    profile = parse_resume(SAMPLE_RESUME_TEXT)
    assert isinstance(profile, CandidateProfile)
    assert profile.name == "JOHN DOE"
    assert "Python" in profile.skills
    assert "FastAPI" in profile.skills
    assert len(profile.experience) >= 1
    assert profile.experience[0].role == "Software Engineer"
    assert profile.experience[0].organization == "Acme Technologies"
    assert len(profile.education) >= 1
    assert profile.education[0].institution == "State University"


def test_build_candidate_profile_custom_target_roles():
    custom_roles = ["AI Engineer", "MLOps Engineer"]
    profile = build_candidate_profile(SAMPLE_RESUME_TEXT, target_roles=custom_roles)
    assert profile.target_roles == custom_roles

