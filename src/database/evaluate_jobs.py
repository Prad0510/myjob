import os
import json
import numpy as np
from dotenv import load_dotenv

from src.database.match_repository import save_match
from src.database.connection import get_connection
from src.database.user_repository import get_all_active_users_with_profiles
from src.matching.job_matcher import match_job
from src.ml.technical_filter import detect_technical_role, detect_technical_skills
from src.embeddings import embed_text
from src.jobs.clustering import cluster_jobs, assign_candidate_to_cluster
from src.notifications.telegram import send_telegram_message
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("evaluate")

TOP_N_MATCHES = int(os.getenv("TOP_N_MATCHES", 5))
CANDIDATE_PROFILE_PATH = os.getenv("CANDIDATE_PROFILE_PATH", "data/processed/candidate_profile.json")


def is_job_technical(title: str, description: str) -> bool:
    """Isolate technical software/engineering jobs from HR, sales, or support."""
    if detect_technical_role(title):
        return True
    skill_count = detect_technical_skills(title, description or "")
    if skill_count >= 1 and any(
        w in title.lower() for w in ["engineer", "developer", "architect", "programmer", "intern"]
    ):
        return True
    return False


def load_candidate_representation(profile_data: dict) -> tuple[str, np.ndarray]:
    """Builds a rich textual representation and dense embedding for candidate."""
    parts = []
    if profile_data.get("name"):
        parts.append(profile_data["name"])
    if profile_data.get("target_roles"):
        parts.append("Target Roles: " + ", ".join(profile_data["target_roles"]))
    if profile_data.get("skills"):
        parts.append("Skills: " + ", ".join(profile_data["skills"]))
    for exp in profile_data.get("experience", []):
        parts.append(f"{exp.get('role', '')} at {exp.get('organization', '')}. {exp.get('description', '')}")
    for proj in profile_data.get("projects", []):
        techs = ", ".join(proj.get("technologies", []))
        parts.append(f"{proj.get('name', '')}. Technologies: {techs}. {proj.get('description', '')}")

    cand_text = " ".join(filter(None, parts))
    if not cand_text.strip():
        cand_text = "Software Engineer Python Developer"

    cand_emb = embed_text(cand_text)
    return cand_text, cand_emb


def fetch_active_technical_jobs():
    """Retrieve all active technical jobs and their embeddings."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    company,
                    location,
                    skills,
                    experience_required,
                    description,
                    application_url
                FROM jobs
                WHERE status = 'active'
                ORDER BY id;
                """
            )
            all_jobs = cursor.fetchall()
    finally:
        connection.close()

    tech_jobs = [job for job in all_jobs if is_job_technical(job[1], job[6] or "")]

    if not tech_jobs:
        return [], None, None, None, []

    job_texts = []
    for job in tech_jobs:
        parts = [job[1]]
        if job[4]:
            parts.append(" ".join(job[4]))
        if job[6]:
            parts.append(job[6][:1500])
        job_texts.append(" ".join(parts))

    job_embs = embed_text(job_texts)
    labels, centroids, unique_labels = cluster_jobs(job_embs)
    return tech_jobs, job_embs, labels, centroids, unique_labels


def evaluate_single_candidate(
    user_id: int | None,
    telegram_chat_id: int | None,
    candidate_profile_data: dict,
    tech_jobs: list,
    job_embs: np.ndarray,
    labels: np.ndarray,
    centroids: np.ndarray,
    unique_labels: list,
) -> int:
    """Matches a specific candidate against active job clusters and sends notifications."""
    if not tech_jobs or job_embs is None:
        return 0

    cand_text, cand_emb = load_candidate_representation(candidate_profile_data)
    candidate_skills = candidate_profile_data.get("skills", [])
    target_roles = candidate_profile_data.get("target_roles", [])
    candidate_experience = " ".join(
        f"{item.get('role', '')} at {item.get('organization', '')}. {item.get('description', '')}"
        for item in candidate_profile_data.get("experience", [])
    )
    candidate_projects = " ".join(
        f"{item.get('name', '')}. Technologies: {', '.join(item.get('technologies', []))}. {item.get('description', '')}"
        for item in candidate_profile_data.get("projects", [])
    )

    best_cluster = assign_candidate_to_cluster(cand_emb, centroids, unique_labels)

    if best_cluster == -1:
        candidate_pool_jobs = tech_jobs
        candidate_pool_embs = job_embs
    else:
        cluster_mask = labels == best_cluster
        candidate_pool_jobs = [tech_jobs[i] for i in range(len(tech_jobs)) if cluster_mask[i]]
        candidate_pool_embs = job_embs[cluster_mask]

    cand_norm = cand_emb / np.linalg.norm(cand_emb)
    job_norms = candidate_pool_embs / np.linalg.norm(candidate_pool_embs, axis=1, keepdims=True)
    sims = np.dot(job_norms, cand_norm)

    top_k = min(TOP_N_MATCHES, len(candidate_pool_jobs))
    top_indices = np.argsort(-sims)[:top_k]

    new_matches_count = 0

    for idx in top_indices:
        job = candidate_pool_jobs[idx]
        similarity = float(sims[idx])

        job_id = job[0]
        title = job[1]
        company = job[2]
        location = job[3]
        skills = job[4] or []
        exp_req = job[5] or ""
        desc = job[6] or ""
        app_url = job[7] or ""

        match_breakdown = match_job(
            candidate_skills=candidate_skills,
            job_title=title,
            job_skills=skills,
            experience_required=exp_req,
            target_roles=target_roles,
            job_description=desc,
            candidate_experience=candidate_experience,
            candidate_projects=candidate_projects,
        )

        final_percent = round(similarity * 100, 1)

        saved = save_match(
            {
                "job_id": job_id,
                "final_score": final_percent,
                "matched_skills": match_breakdown.get("matched_skills", []),
                "missing_skills": match_breakdown.get("missing_skills", []),
                "role_score": match_breakdown.get("role_score", 0),
                "skill_score": match_breakdown.get("skill_score", 0),
                "experience_score": match_breakdown.get("experience_score", 0),
                "semantic_score": round(similarity * 100, 2),
                "application_url": app_url,
            },
            user_id=user_id,
        )

        if saved:
            new_matches_count += 1
            logger.info(f"Match saved for user {user_id}: {title} at {company}")

            # Consumer-friendly message (does NOT reveal backend modules or algorithms)
            matched_skills_str = ", ".join(match_breakdown.get("matched_skills", [])[:5]) or "Technical alignment"
            location_str = location if location else "Remote / Flexible"

            message = (
                f"🎯 <b>New Opportunity Matched!</b>\n\n"
                f"📌 <b>Role:</b> {title}\n"
                f"🏢 <b>Company:</b> {company}\n"
                f"📍 <b>Location:</b> {location_str}\n\n"
                f"⭐️ <b>Profile Match:</b> {final_percent}%\n"
                f"✨ <b>Key Matching Skills:</b> {matched_skills_str}\n\n"
                f"🔗 <a href=\"{app_url}\"><b>View Role & Apply Here</b></a>"
            )

            try:
                send_telegram_message(message, chat_id=telegram_chat_id)
            except Exception as e:
                logger.error(f"Failed to send Telegram message to {telegram_chat_id}: {e}")

    return new_matches_count


def evaluate_user_jobs(user_id: int) -> int:
    """Evaluate jobs specifically for one registered user (e.g. immediately after upload)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.telegram_chat_id, cp.profile_data
                FROM users u
                JOIN candidate_profiles cp ON cp.user_id = u.id
                WHERE u.id = %s;
                """,
                (user_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return 0

    uid, chat_id, profile_data = row
    if isinstance(profile_data, str):
        profile_data = json.loads(profile_data)

    tech_jobs, job_embs, labels, centroids, unique_labels = fetch_active_technical_jobs()
    return evaluate_single_candidate(
        user_id=uid,
        telegram_chat_id=chat_id,
        candidate_profile_data=profile_data,
        tech_jobs=tech_jobs,
        job_embs=job_embs,
        labels=labels,
        centroids=centroids,
        unique_labels=unique_labels,
    )


def evaluate_jobs(job_ids: list[int] | None = None):
    """
    Multi-tenant job matching across all registered users.
    Called by the sync/scheduler pipeline when new jobs arrive.
    """
    active_users = get_all_active_users_with_profiles()
    tech_jobs, job_embs, labels, centroids, unique_labels = fetch_active_technical_jobs()

    if not tech_jobs:
        logger.warning("No technical jobs available to evaluate.")
        return

    # If users exist in database, evaluate for each active user
    if active_users:
        logger.info(f"Evaluating opportunities for {len(active_users)} registered users...")
        for user in active_users:
            evaluate_single_candidate(
                user_id=user["user_id"],
                telegram_chat_id=user["telegram_chat_id"],
                candidate_profile_data=user["profile_data"],
                tech_jobs=tech_jobs,
                job_embs=job_embs,
                labels=labels,
                centroids=centroids,
                unique_labels=unique_labels,
            )
    else:
        # Fallback to local candidate profile file if no multi-tenant users are registered yet
        if os.path.exists(CANDIDATE_PROFILE_PATH):
            with open(CANDIDATE_PROFILE_PATH, "r", encoding="utf-8") as f:
                local_profile = json.load(f)
            evaluate_single_candidate(
                user_id=None,
                telegram_chat_id=None,
                candidate_profile_data=local_profile,
                tech_jobs=tech_jobs,
                job_embs=job_embs,
                labels=labels,
                centroids=centroids,
                unique_labels=unique_labels,
            )


if __name__ == "__main__":
    evaluate_jobs()
