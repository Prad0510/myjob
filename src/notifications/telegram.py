import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_telegram_message(message: str, chat_id: int | str | None = None) -> bool:
    """Send Telegram message. If chat_id is omitted, defaults to TELEGRAM_CHAT_ID in .env."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    target_chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")

    if not target_chat_id:
        raise ValueError("Target chat_id is not specified and TELEGRAM_CHAT_ID is not set in .env")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": target_chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")

    return True
