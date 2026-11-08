"""Telegram Bot Service for Multi-User Resume Upload and Matching.

Allows users to:
1. Start the bot (/start, /help)
2. Send their resume as a PDF file
3. Automatically parse the resume, store candidate profile
4. Trigger immediate recommendations of top matched roles
"""

import os
import io
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

import pymupdf
from src.resume.resume_parser import build_candidate_profile
from src.database.user_repository import get_or_create_user, upsert_candidate_profile
from src.database.evaluate_jobs import evaluate_user_jobs
from src.notifications.telegram import send_telegram_message
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("telegram_bot")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
DOWNLOAD_BASE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}"

RESUME_STORAGE_DIR = Path("data/resumes")
RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_updates(offset: int | None = None, timeout: int = 30) -> list:
    """Long-polling for Telegram updates."""
    url = f"{API_BASE_URL}/getUpdates"
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset

    try:
        res = requests.get(url, params=params, timeout=timeout + 5)
        if res.status_code == 200:
            data = res.json()
            if data.get("ok"):
                return data.get("result", [])
    except Exception as e:
        logger.error(f"Error fetching updates from Telegram: {e}")
    return []


def download_file(file_id: str, dest_path: Path) -> bool:
    """Download a file sent by user in Telegram."""
    try:
        info_url = f"{API_BASE_URL}/getFile?file_id={file_id}"
        info_res = requests.get(info_url, timeout=15)
        info_data = info_res.json()

        if not info_data.get("ok"):
            logger.error(f"Failed to get file info: {info_data}")
            return False

        file_path = info_data["result"]["file_path"]
        download_url = f"{DOWNLOAD_BASE_URL}/{file_path}"

        file_res = requests.get(download_url, timeout=30)
        if file_res.status_code == 200:
            dest_path.write_bytes(file_res.content)
            return True
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}")
    return False


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract plain text from PDF in memory."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    blocks = []
    for page in doc:
        page_blocks = page.get_text("blocks")
        for b in page_blocks:
            text = b[4].strip()
            if text:
                blocks.append(text)
    doc.close()
    return "\n".join(blocks)


def handle_start(chat_id: int, first_name: str):
    welcome_text = (
        f"👋 <b>Welcome, {first_name}!</b>\n\n"
        "I am your personal job matching assistant. I automatically search and match open software & tech opportunities tailored to your skillset.\n\n"
        "📄 <b>How to get started:</b>\n"
        "Simply send me your <b>Resume (as a PDF document)</b> right here in the chat.\n\n"
        "I'll analyze your profile, match you with current active roles, and notify you as soon as matching opportunities appear!"
    )
    send_telegram_message(welcome_text, chat_id=chat_id)


def handle_document(chat_id: int, user_info: dict, doc: dict):
    file_name = doc.get("file_name", "resume.pdf")
    mime_type = doc.get("mime_type", "")

    if not file_name.lower().endswith(".pdf") and "pdf" not in mime_type.lower():
        send_telegram_message(
            "⚠️ Please upload your resume in <b>PDF format</b> so I can analyze it accurately.",
            chat_id=chat_id,
        )
        return

    send_telegram_message(
        "⏳ <b>Analyzing your resume...</b>\nExtracting your technical skills and experience. Please hold on.",
        chat_id=chat_id,
    )

    file_id = doc.get("file_id")
    save_path = RESUME_STORAGE_DIR / f"{chat_id}_{int(time.time())}.pdf"

    if not download_file(file_id, save_path):
        send_telegram_message(
            "❌ Sorry, I couldn't download your document. Please try sending it again.",
            chat_id=chat_id,
        )
        return

    try:
        # Extract text & build candidate profile
        pdf_bytes = save_path.read_bytes()
        resume_text = extract_text_from_pdf_bytes(pdf_bytes)

        if not resume_text.strip():
            send_telegram_message(
                "⚠️ I couldn't read the text inside your PDF. Please ensure it's not a scanned image.",
                chat_id=chat_id,
            )
            return

        candidate_profile = build_candidate_profile(resume_text)

        # Register or update user in database
        user = get_or_create_user(
            telegram_chat_id=chat_id,
            username=user_info.get("username"),
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
        )

        upsert_candidate_profile(
            user_id=user["id"],
            name=candidate_profile.name or user_info.get("first_name", "Candidate"),
            skills=candidate_profile.skills,
            target_roles=candidate_profile.target_roles,
            profile_data=candidate_profile.to_dict(),
            resume_filename=file_name,
        )

        detected_skills = ", ".join(candidate_profile.skills[:8]) if candidate_profile.skills else "General Tech"
        detected_roles = ", ".join(candidate_profile.target_roles[:3])

        success_msg = (
            "✅ <b>Profile Created Successfully!</b>\n\n"
            f"👤 <b>Name:</b> {candidate_profile.name or 'Candidate'}\n"
            f"🎯 <b>Target Roles:</b> {detected_roles}\n"
            f"🛠 <b>Top Skills Identified:</b> {detected_skills}\n\n"
            "🔍 <i>Matching your profile against active job openings now...</i>"
        )
        send_telegram_message(success_msg, chat_id=chat_id)

        # Run personalized matching for this user
        matches_found = evaluate_user_jobs(user["id"])
        if matches_found == 0:
            send_telegram_message(
                "ℹ️ Your profile is saved! We didn't find brand-new matches right this moment, "
                "but you will receive immediate alerts as soon as new matching positions open up.",
                chat_id=chat_id,
            )

    except Exception as e:
        logger.error(f"Error processing resume for chat {chat_id}: {e}", exc_info=True)
        send_telegram_message(
            "❌ An unexpected error occurred while processing your resume. Please try again in a moment.",
            chat_id=chat_id,
        )


def run_bot_polling():
    """Start listening for Telegram messages and resume uploads."""
    logger.info("Starting Telegram Bot listener...")
    offset = None

    while True:
        try:
            updates = get_updates(offset=offset, timeout=25)
            for update in updates:
                offset = update["update_id"] + 1

                message = update.get("message")
                if not message:
                    continue

                chat = message.get("chat", {})
                chat_id = chat.get("id")
                from_user = message.get("from", {})

                if not chat_id:
                    continue

                # Handle text commands
                text = message.get("text", "").strip()
                if text.startswith("/start") or text.startswith("/help"):
                    handle_start(chat_id, from_user.get("first_name", "there"))
                    continue

                # Handle document / resume upload
                document = message.get("document")
                if document:
                    handle_document(chat_id, from_user, document)
                    continue

                # Default fallback for random text messages
                send_telegram_message(
                    "💡 To get job recommendations, please upload your resume as a <b>PDF document</b> in this chat.",
                    chat_id=chat_id,
                )

        except KeyboardInterrupt:
            logger.info("Telegram Bot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error in Telegram Bot polling loop: {e}", exc_info=True)
            time.sleep(3)


if __name__ == "__main__":
    run_bot_polling()

