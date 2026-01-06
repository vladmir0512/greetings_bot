import requests
import json
from typing import Optional

from config import settings

YONOTE_BASE_URL = 'https://unikeygroup.yonote.ru/api/v2'

# ID полей из Yonote
TITLE_FIELD = "title"
TELEGRAM_ID_FIELD = "62c3450b-0a2c-4ba9-8f50-7a48f75a0625"
BIRTHDAY_FIELD = "6ac47e39-270c-41cf-9ca1-1be20bf593da"

def add_application_to_yonote(full_name: str, telegram_id: int, birthday: Optional[str] = None) -> bool:
    """
    Добавить заявку в Yonote базу данных.

    Args:
        full_name: Полное имя пользователя
        telegram_id: Telegram ID
        birthday: День рождения (опционально)

    Returns:
        True если успешно, False иначе
    """
    if not settings.yonote_api_key or not settings.yonote_database_id:
        print("Yonote API key или database ID не настроены")
        return False

    url = f"{YONOTE_BASE_URL}/database/rows"
    headers = {
        "Authorization": f"Bearer {settings.yonote_api_key}",
        "Content-Type": "application/json"
    }

    # Подготавливаем данные
    data = {
        "parentDocumentId": settings.yonote_database_id,
        "collectionId": "1196a54b-fe1b-497f-8f63-d87e86f74bf4",  # Из JSON
        "title": full_name,
        "values": {
            TELEGRAM_ID_FIELD: telegram_id
        }
    }

    if birthday:
        data["values"][BIRTHDAY_FIELD] = birthday

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False))
        if response.status_code == 200 or response.status_code == 201:
            print(f"Заявка для {full_name} успешно добавлена в Yonote")
            return True
        else:
            print(f"Ошибка при добавлении в Yonote: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Исключение при работе с Yonote API: {e}")
        return False