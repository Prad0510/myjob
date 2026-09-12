import re

from src.resume.candidate_profile import (
    CandidateProfile,
    Education,
    Experience,
    Project,
)


def split_into_sections(text: str) -> dict:
    """
    Split resume text into logical sections based on headings.
    """

    section_names = [
        "ABOUT ME",
        "EDUCATION",
        "SKILLS",
        "WORK EXPERIENCE",
        "PROJECTS",
    ]

    sections = {}
    current_section = "HEADER"
    sections[current_section] = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        normalized = line.upper()

        if normalized in section_names:
            current_section = normalized
            sections[current_section] = []
        else:
            sections[current_section].append(line)

    return {
        section: "\n".join(content)
        for section, content in sections.items()
    }


def extract_name(text: str) -> str:
    """
    Extract the candidate name from the beginning of the resume.
    """

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Ignore obvious contact information
        if "@" in line:
            continue

        if re.search(r"\+?\d[\d\s-]{8,}", line):
            continue

        if line.upper() in {
            "ABOUT ME",
            "EDUCATION",
            "SKILLS",
            "WORK EXPERIENCE",
            "PROJECTS",
        }:
            continue
        
        # Skip skill-category lines
        if ":" in line:
            continue
        
        # First suitable line is assumed to be the name
        if re.fullmatch(r"[A-Za-z]+(?:\s+[A-Za-z]+)+", line):
            return line

    return ""


def extract_skills(sections: dict) -> list[str]:
    """
    Extract skills from the skill-category lines in the resume.
    """

    skills = []

    skills_text = sections.get("SKILLS", "")

    for line in skills_text.splitlines():
        if ":" not in line:
            continue

        category, skill_text = line.split(":", 1)

        # Only treat known skill categories as skill information
        if category.strip().lower() in {
            "languages & database",
            "frameworks & libraries",
            "tools & platforms",
        }:
            for skill in skill_text.split(","):
                skill = skill.strip()

                if skill:
                    skills.append(skill)

    return skills

def extract_education(sections: dict) -> list[Education]:
    """
    Extract education details from the EDUCATION section.
    """

    education_text = sections.get("EDUCATION", "")

    if not education_text:
        return []

    lines = [
        line.strip()
        for line in education_text.splitlines()
        if line.strip()
    ]

    
    
    start_year = "" 
    end_year = ""
    
    year_index = None
    
    for i, line in enumerate(lines): 
        match = re.search( 
            r"(20\d{2})\s*-\s*(20\d{2})", 
            line 
        )
        
        if match:
            start_year = match.group(1) 
            end_year = match.group(2) 
            year_index = i 
            break
    
    if year_index is not None:
        lines.pop(year_index)
        
    if len(lines) < 2:
        return []

    institution = lines[0]
    degree = lines[1]

    # Remove extra information from the degree
    degree = re.sub(r"\s*\(.*?\)", "", degree).strip()

    return [
        Education(
            degree=degree,
            institution=institution,
            start_year=start_year,
            end_year=end_year,
        )
    ]
    
def extract_experience(sections: dict) -> list[Experience]:
    """
    Extract work experience from the WORK EXPERIENCE section.
    """

    experience_text = sections.get("WORK EXPERIENCE", "")

    if not experience_text:
        return []

    lines = [
        line.strip()
        for line in experience_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return []

    role = lines[0]
    duration = ""
    organization = ""
    description_lines = []

    # Look for a date such as JUNE 2025
    for i, line in enumerate(lines[1:], start=1):
        if re.search(
            r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|"
            r"AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{4}",
            line.upper(),
        ):
            duration = line
            continue

        # Detect the organization from the known organization-style line.
        if "L&T Skill Trainers Academy" in line:
            organization = line
            continue

        description_lines.append(line)

    return [
        Experience(
            role=role,
            organization=organization,
            duration=duration,
            description=" ".join(description_lines),
        )
    ]
    
def extract_projects(sections: dict) -> list[Project]:
    """
    Extract projects from the PROJECTS section.
    """

    projects_text = sections.get("PROJECTS", "")

    if not projects_text:
        return []

    lines = [
        line.strip()
        for line in projects_text.splitlines()
        if line.strip()
    ]

    projects = []
    current_project = None
    description_lines = []
    technologies = []

    for line in lines:

        # A new project is identified by a "Tech stack:" line
        # completing the previous project.
        if line.lower().startswith("tech stack:"):
            tech_text = line.split(":", 1)[1]

            technologies = [
                tech.strip()
                for tech in tech_text.split(",")
                if tech.strip()
            ]

            if current_project:
                projects.append(
                    Project(
                        name=current_project,
                        technologies=technologies,
                        description=" ".join(description_lines),
                    )
                )

            current_project = None
            description_lines = []
            technologies = []

            continue

        # Ignore GitHub labels
        if line.lower() == "github":
            continue

        # The first line of a project is its name.
        if current_project is None:
            current_project = line
        else:
            description_lines.append(line)

    # Handle the final project if it has no following Tech stack line
    if current_project:
        projects.append(
            Project(
                name=current_project,
                technologies=technologies,
                description=" ".join(description_lines),
            )
        )

    return projects

def parse_resume(text: str) -> CandidateProfile:
    """
    Convert raw resume text into a CandidateProfile.
    """

    sections = split_into_sections(text)

    profile = CandidateProfile(
        name=extract_name(text),
        skills=extract_skills(sections),
        education=extract_education(sections),
        experience=extract_experience(sections),
        projects=extract_projects(sections),
    )

def build_candidate_profile(text: str) -> CandidateProfile:
    """
    Convert extracted resume text into a CandidateProfile.
    """

    sections = split_into_sections(text)

    return CandidateProfile(
        name=extract_name(text),
        skills=extract_skills(sections),
        education=extract_education(sections),
        experience=extract_experience(sections),
        projects=extract_projects(sections),
        target_roles=[
            "Python Developer",
            "Backend Developer",
            "Software Engineer",
            "Data Engineer",
            "Java Developer",
        ],
    )

