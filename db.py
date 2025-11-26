import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional


class ApplicationRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    answers_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    admin_comment TEXT,
                    synced_to_sheet INTEGER DEFAULT 0
                );
                """
            )
            # добавляем колонку при обновлении схемы на существующей базе
            columns = {
                row["name"]
                for row in self._conn.execute("PRAGMA table_info(applications)")
            }
            if "synced_to_sheet" not in columns:
                self._conn.execute(
                    "ALTER TABLE applications ADD COLUMN synced_to_sheet INTEGER DEFAULT 0"
                )
            self._conn.commit()
    def list_all(self) -> List[sqlite3.Row]:
        with self._lock:
            cursor = self._conn.execute(
                "SELECT * FROM applications ORDER BY created_at ASC"
            )
            return cursor.fetchall()
    def save_application(
        self,
        user_id: int,
        chat_id: int,
        username: Optional[str],
        full_name: Optional[str],
        answers: Dict[str, Any],
    ) -> int:
        with self._lock:
            cursor = self._conn.execute(
                """
                INSERT INTO applications (user_id, chat_id, username, full_name, answers_json, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
                """,
                (user_id, chat_id, username, full_name, json.dumps(answers, ensure_ascii=False)),
            )
            self._conn.commit()
            return int(cursor.lastrowid)

    def list_pending(self, limit: int = 10) -> List[sqlite3.Row]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT * FROM applications
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (limit,),
            )
            return cursor.fetchall()

    def get_by_id(self, app_id: int) -> Optional[sqlite3.Row]:
        with self._lock:
            cursor = self._conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
            return cursor.fetchone()

    def get_last_for_user(self, user_id: int) -> Optional[sqlite3.Row]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT * FROM applications
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (user_id,),
            )
            return cursor.fetchone()
    def list_by_user(self, user_id: int) -> List[sqlite3.Row]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT *
                FROM applications
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    def update_status(self, app_id: int, status: str, admin_comment: Optional[str] = None) -> None:
        with self._lock:
            self._conn.execute(
                """
                UPDATE applications
                SET status = ?, admin_comment = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, admin_comment, app_id),
            )
            self._conn.commit()

    def mark_synced(self, app_id: int) -> None:
        with self._lock:
            self._conn.execute(
                """
                UPDATE applications
                SET synced_to_sheet = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (app_id,),
            )
            self._conn.commit()

