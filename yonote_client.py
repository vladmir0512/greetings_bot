import requests
import json
from typing import Optional

from config import settings

YONOTE_BASE_URL = 'https://unikeygroup.yonote.ru/api/v2'

# ID полей из Yonote
TITLE_FIELD = "title"
TELEGRAM_ID_FIELD = "62c3450b-0a2c-4ba9-8f50-7a48f75a0625"
AGE_FIELD = "6ac47e39-270c-41cf-9ca1-1be20bf593da"
TIME_FIELD = "715f0dc5-2090-4483-9b3c-6d582ba70fd9"
EXPERIENCE_FIELD = "63ba2c6b-ba05-431b-888b-fca6b78f14c4"
GOALS_FIELD = "6d96cb26-bf22-4356-be24-2132264f644f"

def add_application_to_yonote(full_name: str, telegram_id: int, age: Optional[str] = None, time: Optional[str] = None, experience: Optional[str] = None, goals: Optional[str] = None) -> bool:
    """
    Добавить заявку в Yonote базу данных.

    Args:
        full_name: Полное имя пользователя
        telegram_id: Telegram ID
        age: Возраст
        time: Свободное время
        experience: Портфолио
        goals: Мотив

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
        "documentId": settings.yonote_database_id,
        "title": full_name,
        "values": {
            TELEGRAM_ID_FIELD: telegram_id
        }
    }

    if age:
        data["values"][AGE_FIELD] = age
    if time:
        data["values"][TIME_FIELD] = time
    if experience:
        data["values"][EXPERIENCE_FIELD] = experience
    if goals:
        data["values"][GOALS_FIELD] = goals

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