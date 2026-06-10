## Overview

A Telegram bot that uploads exercise set data from messages to Google Sheets.

## Setup

1. Create a bot with BotFather and get your token.
2. Create a Google Cloud service account, download the JSON key file, and share your target sheet with the service account email.
3. Create a `.json` config file (and set `USERS_CONFIG_FILE`) with your users:

```json
{
  "users": [
    {
      "telegram_username": "your_username",
      "sheet_id": "YOUR_SHEET_ID",
      "worksheet_name": "Sheet1"
    },
    {
      "telegram_username": "another_user",
      "sheet_id": "ANOTHER_SHEET_ID",
      "worksheet_name": "Sets"
    }
  ]
}
```

4. Create .env file and set the environment variables:

```powershell
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN"
GOOGLE_SERVICE_ACCOUNT_FILE = "C:\\path\\to\\service-account.json"
USERS_CONFIG_FILE = "C:\\path\\to\\config.json"
```

5. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```
