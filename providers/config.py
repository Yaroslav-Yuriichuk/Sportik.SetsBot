from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    token: str
    service_account_file: str


@dataclass(frozen=True)
class UserConfig:
    username: str
    sheet_id: str
    worksheet_name: str


@dataclass(frozen=True)
class UsersConfig:
    users: dict[str, UserConfig]

    def has_user_config(self, username: str) -> bool:
        return username in self.users

    def get_user_config(self, username: str) -> UserConfig | None:
        return self.users.get(username)


class ConfigProvider:
    def __init__(self, users_config_path: str | None = None) -> None:
        self._users_config_path = users_config_path or os.environ.get("USERS_CONFIG_FILE")

    def get_app_config(self) -> AppConfig:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        service_account_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")

        if not token:
            raise SystemExit("Missing TELEGRAM_BOT_TOKEN environment variable.")

        if not service_account_file:
            raise SystemExit("Missing GOOGLE_SERVICE_ACCOUNT_FILE environment variable.")

        return AppConfig(
            token=token,
            service_account_file=service_account_file,
        )

    def get_user_configs(self) -> UsersConfig:
        users_config_path = self._users_config_path

        try:
            with open(users_config_path, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            raise SystemExit(f"Missing configuration file: {users_config_path}")
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON in configuration file: {exc}")

        users = config.get("users")

        if not isinstance(users, list):
            raise SystemExit("Configuration must include 'users' list.")

        user_configs: dict[str, UserConfig] = {}

        for index, user in enumerate(users, start=1):
            if not isinstance(user, dict):
                raise SystemExit(f"User entry #{index} must be an object.")

            username = user.get("telegram_username")
            sheet_id = user.get("sheet_id")
            worksheet_name = user.get("worksheet_name", "Sets")

            if not isinstance(username, str) or not username.strip():
                raise SystemExit("Each user must include a non-empty telegram_username.")

            if username in user_configs:
                raise SystemExit(f"Duplicate telegram_username found: {username}")

            user_configs[username] = UserConfig(
                username=username,
                sheet_id=sheet_id,
                worksheet_name=worksheet_name,
            )

        return UsersConfig(
            users=user_configs,
        )
