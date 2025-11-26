import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _split_env_list(value: str | None) -> List[int]:
    if not value:
        return []
    raw_values = [item.strip() for item in value.split(",")]
    return [int(item) for item in raw_values if item.isdigit()]


@dataclass(slots=True)
class Settings:
    bot_token: str = field(default_factory=lambda: os.environ.get("BOT_TOKEN", ""))
    database_path: Path = field(
        default_factory=lambda: Path(os.environ.get("DATABASE_PATH", "data/applications.db"))
    )
    admin_ids: List[int] = field(default_factory=lambda: _split_env_list(os.environ.get("ADMIN_IDS")))
    google_credentials_file: str | None = field(default_factory=lambda: os.environ.get("GOOGLE_CREDENTIALS_FILE"))
    google_sheet_id: str | None = field(default_factory=lambda: os.environ.get("GOOGLE_SHEET_ID"))
    community_invite_link: str | None = field(default_factory=lambda: os.environ.get("COMMUNITY_INVITE_LINK"))

    def validate(self) -> None:
        if not self.bot_token:
            raise ValueError("Переменная окружения BOT_TOKEN не задана.")
        if not self.admin_ids:
            raise ValueError("Список администраторов ADMIN_IDS не задан или пуст.")


settings = Settings()

