import requests
import logging

# Настройки
BASE_URL = "https://app.yonote.ru/api"
TOKEN = "I2xRjznMsl5NnGwL3Sez2vruQrTJPxIlywCMrv"
COLLECTION_ID = "646bf24c-bb56-4649-b290-2d11a0360cc8"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_document(text, title="Новый документ"):
    """
    Создаёт новый документ в коллекции с текстом.

    :param text: Текст документа
    :param title: Заголовок документа
    :return: Словарь с данными документа или None при ошибке
    """
    url = f"{BASE_URL}/documents.create"
    payload = {
        "title": title,
        "text": text,
        "collectionId": COLLECTION_ID,
        "token": TOKEN,
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


if __name__ == "__main__":
    doc = create_document("🐍 Привет! Этот текст точно появится в документе", "Документ бота")
    if doc:
        print(f"Создан документ: {doc['id']}, URL: {doc['url']}")
