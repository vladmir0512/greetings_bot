import unittest
import sqlite3
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Добавляем путь к основному коду
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import ApplicationRepository

class TestDatabase(unittest.TestCase):
    """Тесты для работы с базой данных"""

    def setUp(self):
        """Создание временной базы данных для тестов"""
        self.test_db_path = Path(':memory:')  # Используем in-memory базу для тестов
        self.repo = ApplicationRepository(self.test_db_path)
        
    def tearDown(self):
        """Закрытие подключения к базе данных"""
        # For in-memory, no need to close explicitly, but ensure
        pass

    def test_save_application(self):
        """Тест добавления заявки"""
        # Добавляем тестовую заявку
        user_id = 123456789
        chat_id = 123456
        username = "testuser"
        full_name = "Test User"
        answers = {"city": "Test City", "experience": "None", "goal": "Testing"}
        
        app_id = self.repo.save_application(user_id, chat_id, username, full_name, answers)
        
        # Проверяем, что заявка добавлена
        app = self.repo.get_by_id(app_id)
        
        self.assertIsNotNone(app)
        self.assertEqual(app['user_id'], user_id)
        self.assertEqual(app['chat_id'], chat_id)
        self.assertEqual(app['username'], username)
        self.assertEqual(app['full_name'], full_name)
        self.assertEqual(app['status'], 'pending')

    def test_list_pending_applications(self):
        """Тест получения заявок на рассмотрение"""
        # Добавляем тестовую заявку
        answers = {"city": "Test City", "experience": "None", "goal": "Testing"}
        self.repo.save_application(123456789, 123456, "testuser", "Test User", answers)
        
        # Получаем заявки на рассмотрение
        applications = self.repo.list_pending()
        
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0]['full_name'], "Test User")
        self.assertEqual(applications[0]['status'], 'pending')

    def test_update_status(self):
        """Тест обновления статуса заявки"""
        answers = {"city": "Test City"}
        app_id = self.repo.save_application(123456789, 123456, "testuser", "Test User", answers)
        
        self.repo.update_status(app_id, 'approved', 'Approved by admin')
        
        app = self.repo.get_by_id(app_id)
        self.assertEqual(app['status'], 'approved')
        self.assertEqual(app['admin_comment'], 'Approved by admin')

    def test_list_all(self):
        """Тест получения всех заявок"""
        answers = {"city": "Test City"}
        self.repo.save_application(123456789, 123456, "testuser", "Test User", answers)
        
        applications = self.repo.list_all()
        
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0]['full_name'], "Test User")

    def test_get_last_for_user(self):
        """Тест получения последней заявки пользователя"""
        answers = {"city": "Test City"}
        self.repo.save_application(123456789, 123456, "testuser", "Test User", answers)
        
        app = self.repo.get_last_for_user(123456789)
        
        self.assertIsNotNone(app)
        self.assertEqual(app['user_id'], 123456789)

if __name__ == '__main__':
    unittest.main()