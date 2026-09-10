from src.matching.skill_categorizer import categorize_skills


def categorize_job_skills(job_skills: list[str]) -> dict:
    """
    Categorize the skills extracted from a job.
    """

    return categorize_skills(job_skills)