from src.database.match_repository import save_match, match_exists


test_match = {
    "job_id": 4,
    "final_score": 82.50,
    "matched_skills": ["python", "sql"],
    "missing_skills": ["docker"],
    "role_score": 100.0,
    "skill_score": 80.0,
    "experience_score": 50.0,
    "semantic_score": 70.0,
}


print("Before saving:")
print("Match exists:", match_exists(test_match["job_id"]))


print("\nSaving match...")
saved = save_match(test_match)
print("Saved:", saved)


print("\nAfter saving:")
print("Match exists:", match_exists(test_match["job_id"]))