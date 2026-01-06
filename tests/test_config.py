import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Добавляем путь к основному коду
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import load_config

class TestConfig(unittest.TestCase):
    """Тесты для конфигурации бота"""

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='BOT_TOKEN=test_token\nADMIN_IDS=123456789')
    def test_load_config_success(self, mock_file, mock_exists):
        """Тест успешной загрузки конфигурации"""
        mock_exists.return_value = True
        
        config = load_config()
        
        self.assertEqual(config['BOT_TOKEN'], 'test_token')
        self.assertEqual(config['ADMIN_IDS'], [123456789])

    @patch('os.path.exists')
    def test_load_config_file_not_found(self, mock_exists):
        """Тест обработки отсутствия файла конфигурации"""
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError):
            load_config()

if __name__ == '__main__':
    unittest.main()