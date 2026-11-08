import json
from typing import Optional, List, Dict, Any
from src.database.connection import get_connection
from src.utils.logger import get_logger

logger = get_logger("user_repository")


def get_or_create_user(
    telegram_chat_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Get an existing user or insert a new one by telegram_chat_id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (telegram_chat_id, telegram_username, first_name, last_name, is_active, updated_at)
                VALUES (%s, %s, %s, %s, true, CURRENT_TIMESTAMP)
                ON CONFLICT (telegram_chat_id) DO UPDATE
                SET telegram_username = EXCLUDED.telegram_username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id, telegram_chat_id, telegram_username, first_name, last_name, is_active;
                """,
                (telegram_chat_id, username, first_name, last_name),
            )
            row = cur.fetchone()
        conn.commit()
        return {
            "id": row[0],
            "telegram_chat_id": row[1],
            "username": row[2],
            "first_name": row[3],
            "last_name": row[4],
            "is_active": row[5],
        }
    finally:
        conn.close()


def upsert_candidate_profile(
    user_id: int,
    name: str,
    skills: List[str],
    target_roles: List[str],
    profile_data: Dict[str, Any],
    resume_filename: str = "",
) -> int:
    """Save or update candidate profile for a specific user."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO candidate_profiles (
                    user_id, name, skills, target_roles, profile_data, resume_filename, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE
                SET name = EXCLUDED.name,
                    skills = EXCLUDED.skills,
                    target_roles = EXCLUDED.target_roles,
                    profile_data = EXCLUDED.profile_data,
                    resume_filename = EXCLUDED.resume_filename,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
                """,
                (
                    user_id,
                    name,
                    skills,
                    target_roles,
                    json.dumps(profile_data),
                    resume_filename,
                ),
            )
            profile_id = cur.fetchone()[0]
        conn.commit()
        return profile_id
    finally:
        conn.close()


def get_all_active_users_with_profiles() -> List[Dict[str, Any]]:
    """Retrieve all active users who have an uploaded resume profile."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    u.id,
                    u.telegram_chat_id,
                    u.first_name,
                    cp.name,
                    cp.skills,
                    cp.target_roles,
                    cp.profile_data
                FROM users u
                INNER JOIN candidate_profiles cp ON cp.user_id = u.id
                WHERE u.is_active = true
                ORDER BY u.id;
                """
            )
            rows = cur.fetchall()

        results = []
        for r in rows:
            profile_data = r[6]
            if isinstance(profile_data, str):
                profile_data = json.loads(profile_data)
            results.append({
                "user_id": r[0],
                "telegram_chat_id": r[1],
                "first_name": r[2] or "",
                "name": r[3] or "",
                "skills": r[4] or [],
                "target_roles": r[5] or [],
                "profile_data": profile_data or {},
            })
        return results
    finally:
        conn.close()

