import requests
import json
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

YONOTE_BASE_URL = 'https://unikeygroup.yonote.ru/api'

# ID полей из Yonote
TITLE_FIELD = "title"
TELEGRAM_ID_FIELD = "62c3450b-0a2c-4ba9-8f50-7a48f75a0625"
AGE_FIELD = "6ac47e39-270c-41cf-9ca1-1be20bf593da"
TIME_FIELD = "715f0dc5-2090-4483-9b3c-6d582ba70fd9"
EXPERIENCE_FIELD = "63ba2c6b-ba05-431b-888b-fca6b78f14c4"
GOALS_FIELD = "6d96cb26-bf22-4356-be24-2132264f644f"
JOB_FIELD = "placeholder-job-field-id"  # Замените на реальный ID поля в Yonote

def add_application_to_yonote(full_name: str, telegram_id: int, age: Optional[str] = None, experience: Optional[str] = None, portfolio: Optional[str] = None, goals: Optional[str] = None, job: Optional[str] = None) -> bool:
    """
    Добавить заявку в Yonote базу данных.

    Args:
        full_name: Полное имя пользователя
        telegram_id: Telegram ID
        age: Возраст
        experience: Стаж
        portfolio: Ссылки на работы
        goals: Цель
        job: Должность

    Returns:
        True если успешно, False иначе
    """
    logger.info(f"Добавление заявки для {full_name} (Telegram ID: {telegram_id})")
    if not settings.yonote_api_key or not settings.yonote_database_id:
        logger.error("Yonote API key или database ID не настроены")
        print("Yonote API key или database ID не настроены")
        return False

    # Подготавливаем транзакцию
    transaction = {
        "databaseId": settings.yonote_database_id,
        "operations": [
            {
                "type": "create",
                "collectionId": "1196a54b-fe1b-497f-8f63-d87e86f74bf4",
                "title": full_name,
                "values": {
                    TELEGRAM_ID_FIELD: telegram_id
                }
            }
        ]
    }

    values = transaction["operations"][0]["values"]
    if age:
        values[AGE_FIELD] = age
    if experience:
        values[TIME_FIELD] = experience
    if portfolio:
        values[EXPERIENCE_FIELD] = portfolio
    if goals:
        values[GOALS_FIELD] = goals
    if job:
        values[JOB_FIELD] = job

    return perform_transaction(transaction)

def get_yonote_rows():
    """Получить все строки из Yonote database для проверки"""
    logger.info("Получение строк из Yonote database")
    if not settings.yonote_api_key or not settings.yonote_database_id:
        logger.error("Yonote API key или database ID не настроены")
        print("Yonote API key или database ID не настроены")
        return []

    url = f"{YONOTE_BASE_URL}/database/rows"
    headers = {
        "Authorization": f"Bearer {settings.yonote_api_key}",
    }

    params = {
        "filter": json.dumps({"parentDocumentId": settings.yonote_database_id}),
        "limit": 100,
        "offset": 0,
        "sort": '[["tableOrder","ASC"]]',
    }

    logger.info(f"Отправка GET запроса в Yonote API: {url}")
    try:
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"Получен ответ: статус {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Получено {len(data.get('data', []))} строк")
            return data.get("data", [])
        else:
            logger.error(f"Ошибка чтения: {response.status_code} - {response.text}")
            print(f"Ошибка чтения: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Исключение при чтении: {e}")
        print(f"Исключение при чтении: {e}")
        return []

def create_document(full_name: str, age: str, job: str, experience: str, portfolio: str, goals: str, title: str = "Заявка") -> Optional[dict]:
    """
    Создаёт новый документ в коллекции с данными заявки.

    :param full_name: Имя пользователя
    :param age: Возраст
    :param job: Должность
    :param experience: Стаж
    :param portfolio: Портфолио
    :param goals: Цели
    :param title: Заголовок документа
    :return: Словарь с данными документа или None при ошибке
    """
    text = f"""# 🎉 Заявка на вступление в проект

## 👤 Личная информация
👨‍💻 **Имя:** {full_name}

🎂 **Возраст:** {age}

## 💼 Профессиональная информация
🎤 **Должность:** {job}

⏱️ **Стаж:** {experience}

## 🔗 Портфолио и цели
📁 **Портфолио:** {portfolio}

🎯 **Цели:** {goals}
"""
    if not settings.yonote_api_key:
        logger.error("Yonote API key не настроен")
        print("Yonote API key не настроен")
        return None

    url = f"{YONOTE_BASE_URL}/documents.create"
    payload = {
        "title": title,
        "text": text,
        "collectionId": "1196a54b-fe1b-497f-8f63-d87e86f74bf4",
        "token": settings.yonote_api_key,
        "publish": True
    }

    logger.info("Создаём новый документ...")
    response = requests.post(url, json=payload)
    logger.info(f"Ответ сервера: {response.status_code} - {response.text}")

    if response.status_code == 200 and response.json().get("ok"):
        doc_data = response.json()["data"]
        logger.info(f"Документ создан: {doc_data['id']}, URL: {doc_data['url']}")
        return doc_data
    else:
        logger.error("Не удалось создать документ")
        return None