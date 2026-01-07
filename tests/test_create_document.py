#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yonote_client import create_document

# Тест создания документа
if __name__ == "__main__":
    full_name = "Тестовый Пользователь"
    age = "25"
    job = "Программист"
    experience = "2 года"
    portfolio = "http://example.com"
    goals = "Научиться работать в команде"
    title = f"Заявка от {full_name}"
    doc = create_document(full_name, age, job, experience, portfolio, goals, title)
    if doc:
        print(f"Dokument sozdan: {doc['id']}, URL: {doc['url']}")
    else:
        print("Oshibka pri sozdanii dokumenta")