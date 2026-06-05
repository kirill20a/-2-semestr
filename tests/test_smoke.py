"""Smoke-тесты: проверка запуска и базовой функциональности"""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import init_db, get_connection


class TestSmoke(unittest.TestCase):
    
    def test_database_init(self):
        """База данных инициализируется без ошибок"""
        init_db()
        conn = get_connection()
        self.assertIsNotNone(conn)
        conn.close()
    
    def test_tables_exist(self):
        """Все таблицы созданы"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cursor.fetchall()]
        expected = ['categories', 'dish_composition', 'employees', 'job_titles',
                    'menu', 'order_items', 'orders', 'products', 'tables_cafe']
        for table in expected:
            self.assertIn(table, tables, f"Таблица {table} не найдена")
        conn.close()
    
    def test_app_imports(self):
        """Все модули импортируются"""
        from src.config import DB_NAME
        from src.models import Dish, Employee, Order
        self.assertTrue(True)
    
    def test_makefile_exists(self):
        """Makefile существует и содержит нужные команды"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Makefile')
        self.assertTrue(os.path.exists(path))
        with open(path, encoding='utf-8') as f:
            content = f.read()
        self.assertIn('help:', content)
        self.assertIn('test:', content)
        self.assertIn('run:', content)


if __name__ == '__main__':
    unittest.main()