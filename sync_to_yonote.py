import json
from config import settings
from db import ApplicationRepository
from yonote_client import add_application_to_yonote

repo = ApplicationRepository(settings.database_path)

# Синхронизировать только не синхронизированные заявки
rows = repo.list_all()
for row in rows:
    synced_flag = row["synced_to_yonote"] if "synced_to_yonote" in row.keys() else 0
    if synced_flag:
        continue  # Уже синхронизирована

    answers = json.loads(row["answers_json"])
    full_name = row["full_name"] or ""
    telegram_id = row["user_id"]
    age = answers.get("age", "")
    time = answers.get("time", "")
    experience = answers.get("experience", "")
    goals = answers.get("goals", "")

    success = add_application_to_yonote(full_name, telegram_id, age, time, experience, goals)
    if success:
        repo.mark_synced(row["id"])
        print(f"Заявка {row['id']} ({full_name}) синхронизирована в Yonote")
    else:
        print(f"Ошибка синхронизации заявки {row['id']}")