import logging
import asyncio
import gspread

from datetime import timezone
from dotenv import load_dotenv
from gspread.utils import ValueInputOption
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from config import ConfigProvider
from parsing import parse_exercise
from sheets import WorksheetProvider


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    sender = update.effective_user
    sender_username = sender.username if sender else None

    if not sender_username:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    config_provider = context.application.bot_data["config_provider"]

    users_config = config_provider.get_user_configs()

    if not users_config.has_user_config(sender_username):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    user_config = users_config.get_user_config(sender_username)

    if not user_config.sheet_id or not user_config.worksheet_name:
        await update.message.reply_text("Configuration for your user is not complete.")
        return

    if update.message:
        await update.message.reply_text(
            "Bot started. Send exercise name and repetitions separated by a comma to log a set."
        )


async def default_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or update.message.text is None:
        return

    sender = update.effective_user
    sender_username = sender.username if sender else None

    if not sender_username:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    parsed = parse_exercise(update.message.text)

    if not parsed:
        await update.message.reply_text(
            "Please send exercise name and repetitions."
        )
        return

    exercise_name, repetitions = parsed
    timestamp = update.message.date.astimezone(timezone.utc).isoformat()

    config_provider = context.application.bot_data["config_provider"]

    users_config = config_provider.get_user_configs()

    if not users_config.has_user_config(sender_username):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    user_config = users_config.get_user_config(sender_username)

    if not user_config.sheet_id or not user_config.worksheet_name:
        await update.message.reply_text("Configuration for your user is not complete.")
        return

    worksheet_provider: WorksheetProvider = context.application.bot_data["worksheet_provider"]
    worksheet = worksheet_provider.get(user_config.sheet_id, user_config.worksheet_name)

    if worksheet is None:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

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


def main() -> None:
    load_dotenv()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    config_provider = ConfigProvider()
    app_config = config_provider.get_app_config()

    gspread_client = gspread.service_account(filename=app_config.service_account_file)
    worksheet_provider = WorksheetProvider(gspread_client)

    application = Application.builder().token(app_config.token).build()
    application.bot_data["config_provider"] = config_provider
    application.bot_data["worksheet_provider"] = worksheet_provider
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, default_reply))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
