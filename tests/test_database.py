"""Тесты работы с базой данных"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import get_connection, init_db, execute_query, execute_insert


class TestDatabase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Создаём тестовую БД"""
        init_db()
    
    def test_tables_created(self):
        """Проверяем создание таблиц"""
        tables = execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        table_names = [t[0] for t in tables]
        
        expected = ['categories', 'dish_composition', 'employees', 
                    'job_titles', 'menu', 'order_items', 
                    'orders', 'products', 'tables_cafe']
        
        for table in expected:
            self.assertIn(table, table_names, f"Таблица {table} не создана")
    
    def test_default_data(self):
        """Проверяем начальные данные"""
        tables = execute_query("SELECT COUNT(*) as cnt FROM tables_cafe")
        self.assertEqual(tables[0][0], 10, "Должно быть 10 столиков")
        
        menu = execute_query("SELECT COUNT(*) as cnt FROM menu")
        self.assertEqual(menu[0][0], 11, "Должно быть 11 блюд")
    
    def test_insert_order(self):
        """Тест создания заказа"""
        order_id = execute_insert(
            "INSERT INTO orders (table_num, id_employee, status) VALUES (?, ?, ?)",
            (1, 1, 'Тест')
        )
        self.assertIsNotNone(order_id)
        self.assertGreater(order_id, 0)


if __name__ == '__main__':
    unittest.main()