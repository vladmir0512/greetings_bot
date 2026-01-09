import unittest
from unittest.mock import patch
import sys
import os

# Добавляем путь к основному коду
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Settings, settings

class TestConfig(unittest.TestCase):
    """Тесты для конфигурации бота"""

    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token', 'ADMIN_IDS': '123456789'})
    def test_settings_success(self):
        """Тест успешной загрузки конфигурации"""
        s = Settings()
        self.assertEqual(s.bot_token, 'test_token')
        self.assertEqual(s.admin_ids, [123456789])

    @patch.dict('os.environ', {}, clear=True)
    def test_settings_missing_env(self):
        """Тест обработки отсутствия переменных окружения"""
        s = Settings()
        self.assertEqual(s.bot_token, '')
        self.assertEqual(s.admin_ids, [])

    def test_settings_validate_success(self):
        """Тест валидации успешной"""
        s = Settings()
        s.bot_token = 'token'
        s.admin_ids = [123]
        s.validate()  # Should not raise

    def test_settings_validate_failure_no_token(self):
        """Тест валидации без токена"""
        s = Settings()
        s.bot_token = ''
        s.admin_ids = [123]
        with self.assertRaises(ValueError):
            s.validate()

    def test_settings_validate_failure_no_admins(self):
        """Тест валидации без админов"""
        s = Settings()
        s.bot_token = 'token'
        s.admin_ids = []
        with self.assertRaises(ValueError):
            s.validate()

if __name__ == '__main__':
    unittest.main()