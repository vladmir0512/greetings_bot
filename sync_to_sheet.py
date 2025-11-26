import json
from config import settings
from db import ApplicationRepository
from google_client import SheetsClient

repo = ApplicationRepository(settings.database_path)
sheets = SheetsClient(settings.google_credentials_file, settings.google_sheet_id)

rows = repo.list_all()  # или напишите свой SELECT для всех заявок
for row in rows:
    answers = json.loads(row["answers_json"])
    payload = {
        "ID": str(row["user_id"]),
        "Имя": row["full_name"] or "",
        "Username": f"@{row['username']}" if row["username"] else "",
        "Город": answers.get("city", ""),
        "Опыт": answers.get("experience", ""),
        "Цель": answers.get("goals", ""),
    }
    success = sheets.append_application(payload)
    print(row["id"], "->", "OK" if success else "FAIL")