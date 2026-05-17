import logging
import os
import asyncio
import gspread

from datetime import timezone
from dotenv import load_dotenv
from gspread.utils import ValueInputOption
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

REPLY_TEXT = "Message received."


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(REPLY_TEXT)


def parse_message(text: str) -> tuple[str, int] | None:
    parts = [part for part in text.strip().split() if part]

    if len(parts) < 2:
        return None

    repetitions_text = parts[-1]

    if not repetitions_text.isdigit():
        return None

    exercise_name = " ".join(parts[:-1]).strip()

    if not exercise_name:
        return None

    return exercise_name, int(repetitions_text)


async def default_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or update.message.text is None:
        return

    parsed = parse_message(update.message.text)

    if not parsed:
        await update.message.reply_text(
            "Please send exercise name and repetitions."
        )
        return

    exercise_name, repetitions = parsed
    timestamp = update.message.date.astimezone(timezone.utc).isoformat()
    worksheet: gspread.Worksheet = context.application.bot_data["worksheet"]

    try:
        await asyncio.to_thread(
            worksheet.append_row,
            [exercise_name, timestamp, repetitions],
            value_input_option=ValueInputOption.raw,
        )
    except Exception:
        logging.exception("Failed to append row to Google Sheet")
        await update.message.reply_text("Failed to log message.")
        return

    await update.message.reply_text(f"Logged {repetitions} repetition(s) of {exercise_name}.")


def build_worksheet() -> gspread.Worksheet:
    service_account_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    worksheet_name = os.environ.get("GOOGLE_WORKSHEET_NAME", "Sets")

    if not service_account_file:
        raise SystemExit("Missing GOOGLE_SERVICE_ACCOUNT_FILE environment variable.")

    if not sheet_id:
        raise SystemExit("Missing GOOGLE_SHEET_ID environment variable.")

    client = gspread.service_account(filename=service_account_file)
    spreadsheet = client.open_by_key(sheet_id)

    return spreadsheet.worksheet(worksheet_name)


def main() -> None:
    load_dotenv()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN environment variable.")

    worksheet = build_worksheet()

    application = Application.builder().token(token).build()
    application.bot_data["worksheet"] = worksheet
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, default_reply))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
