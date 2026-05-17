## Overview

A Telegram bot that uploads exercise set data from messages to Google Sheets.

## Setup

1. Create a bot with BotFather and get your token.
2. Create a Google Cloud service account, download the JSON key file, and share your target sheet with the service account email.
3. Create .env file and set the environment variables:

```powershell
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN"
GOOGLE_SERVICE_ACCOUNT_FILE = "C:\\path\\to\\service-account.json"
GOOGLE_SHEET_ID = "YOUR_SHEET_ID"
GOOGLE_WORKSHEET_NAME = "Sheet1"
ALLOWED_TELEGRAM_USERNAME = "your_username"
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```
