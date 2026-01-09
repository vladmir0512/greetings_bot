import requests
import json
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

YONOTE_BASE_URL = settings.yonote_base_url

def create_document(full_name: str, age: str, job: str, experience: str, portfolio: str, goals: str, username: str, title: str = "Заявка") -> Optional[dict]:
    """
    Создаёт новый документ в коллекции с данными заявки.

    :param full_name: Имя пользователя
    :param age: Возраст
    :param job: Должность
    :param experience: Стаж
    :param portfolio: Портфолио
    :param goals: Цели
    :param username: Telegram username
    :param title: Заголовок документа
    :return: Словарь с данными документа или None при ошибке
    """
    text = f"""# 🎉 Заявка на вступление в проект

## 👤 Личная информация
👨‍💻 **Имя:** {full_name}

📱 **Telegram:** @{username}

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
        "collectionId": settings.yonote_collection_id,
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