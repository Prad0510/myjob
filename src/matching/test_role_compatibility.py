from src.matching.role_compatibility import (
    classify_job_role,
    calculate_role_compatibility
)


target_roles = [
    "Python Developer",
    "Backend Developer",
    "Software Engineer",
    "Data Engineer",
    "Java Developer",
]


test_jobs = [
    "Software Engineer, Backend",
    "Software Engineer, eve",
    "IT Systems Engineer",
    "Product Designer, Marketplace",
    "Account Executive, Majors",
    "Python Backend Intern",
    "Data Engineer",
    "Java Developer",
]


for job in test_jobs:

    role = classify_job_role(job)

    score = calculate_role_compatibility(
        job,
        target_roles
    )

    print(
        f"{job:40} | "
        f"role = {role:10} | "
        f"compatibility = {score}"
    )