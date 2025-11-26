from __future__ import annotations

import logging
from typing import Dict, Optional

try:
    import gspread
except ImportError:  # pragma: no cover - опциональная зависимость
    gspread = None


class SheetsClient:
    def __init__(self, credentials_file: Optional[str], sheet_id: Optional[str]) -> None:
        self._sheet = None
        if not credentials_file or not sheet_id:
            logging.warning("Google Sheets не настроены, пропускаем интеграцию.")
            return
        if not gspread:
            logging.error("Пакет gspread не установлен. Интеграция отключена.")
            return
        try:
            client = gspread.service_account(filename=credentials_file)
            self._sheet = client.open_by_key(sheet_id).sheet1
        except Exception as exc:  # pragma: no cover - инициализация
            logging.exception("Не удалось подключиться к Google Sheets")
            self._sheet = None

    def append_application(self, payload: Dict[str, str]) -> bool:
        if not self._sheet:
            return False
        try:
            self._sheet.append_row(list(payload.values()))
            return True
        except Exception as exc:  # pragma: no cover - вызовы API
            logging.error("Ошибка записи в Google Sheets: %s", exc)
            return False

