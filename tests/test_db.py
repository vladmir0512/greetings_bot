import unittest
import sqlite3
import os
import sys
from unittest.mock import patch, MagicMock

# Добавляем путь к основному коду
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import init_db, add_application, get_pending_applications, update_application_status

class TestDatabase(unittest.TestCase):
    """Тесты для работы с базой данных"""

    def setUp(self):
        """Создание временной базы данных для тестов"""
        self.test_db = ':memory:'  # Используем in-memory базу для тестов
        self.connection = sqlite3.connect(self.test_db)
        
    def tearDown(self):
        """Закрытие подключения к базе данных"""
        self.connection.close()

    @patch('sqlite3.connect')
    def test_init_db(self, mock_connect):
        """Тест инициализации базы данных"""
        mock_connect.return_value = self.connection
        
        init_db()
        
        # Проверяем, что таблица создана
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
        self.assertIsNotNone(cursor.fetchone())

    @patch('sqlite3.connect')
    def test_add_application(self, mock_connect):
        """Тест добавления заявки"""
        mock_connect.return_value = self.connection
        init_db()  # Инициализируем базу перед тестом
        
        # Добавляем тестовую заявку
        user_id = 123456789
        name = "Test User"
        username = "testuser"
        city = "Test City"
        experience = "None"
        goal = "Testing"
        
        add_application(user_id, name, username, city, experience, goal)
        
        # Проверяем, что заявка добавлена
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM applications WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[1], user_id)
        self.assertEqual(result[2], name)
        self.assertEqual(result[3], username)

    @patch('sqlite3.connect')
    def test_get_pending_applications(self, mock_connect):
        """Тест получения заявок на рассмотрение"""
        mock_connect.return_value = self.connection
        init_db()
        
        # Добавляем тестовую заявку
        add_application(123456789, "Test User", "testuser", "Test City", "None", "Testing")
        
        # Получаем заявки на рассмотрение
        applications = get_pending_applications()
        
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0][2], "Test User")

if __name__ == '__main__':
    unittest.main()