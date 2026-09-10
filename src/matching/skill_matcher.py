def compare_skills(
    candidate_skills: list[str],
    job_skills: list[str]
) -> dict:
    """
    Compare candidate skills with the skills
    required/found in a job.
    """

    candidate_set = {
        skill.lower()
        for skill in candidate_skills
    }

    job_set = {
        skill.lower()
        for skill in job_skills
    }

    matched = candidate_set.intersection(job_set)
    missing = job_set.difference(candidate_set)

    return {
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "total_job_skills": len(job_set),
    } 