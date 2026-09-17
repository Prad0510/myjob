from src.notifications.telegram import send_telegram_message


message = (
    "🚀 MyJob Telegram Test\n\n"
    "Telegram notifications are working successfully!"
)

send_telegram_message(message)

print("Telegram message sent successfully.")