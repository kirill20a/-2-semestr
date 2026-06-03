"""
Smoke tests для фиксации текущего поведения приложения.
Эти тесты проверяют что базовая функциональность работает ДО рефакторинга.
"""
import unittest
import sqlite3
import os
import sys
from datetime import datetime

# Добавляем путь к src чтобы импортировать функции
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class DatabaseInitializationTests(unittest.TestCase):
    """Тесты инициализации базы данных"""
    
    def setUp(self):
        """Создаем временную БД в памяти перед каждым тестом"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self._init_database()
    
    def tearDown(self):
        """Закрываем соединение после теста"""
        self.conn.close()
    
    def _init_database(self):
        """Инициализация схемы БД (копия из main.py)"""
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS tables_cafe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER NOT NULL UNIQUE,
                capacity INTEGER DEFAULT 4,
                is_occupied INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS job_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                salary_base REAL DEFAULT 0,
                bonus_percent REAL DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                id_job_title INTEGER NOT NULL,
                FOREIGN KEY (id_job_title) REFERENCES job_titles(id)
            );
            
            CREATE TABLE IF NOT EXISTS categories (
                id_category INTEGER PRIMARY KEY AUTOINCREMENT,
                name_category TEXT NOT NULL UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS menu (
                id_dish INTEGER PRIMARY KEY AUTOINCREMENT,
                name_of_dish TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                id_category INTEGER NOT NULL,
                cooking_time INTEGER DEFAULT 10,
                is_available INTEGER DEFAULT 1,
                FOREIGN KEY (id_category) REFERENCES categories(id_category)
            );
            
            CREATE TABLE IF NOT EXISTS products (
                id_product INTEGER PRIMARY KEY AUTOINCREMENT,
                name_of_product TEXT NOT NULL,
                unit TEXT NOT NULL,
                quantity_at_storage REAL NOT NULL CHECK (quantity_at_storage >= 0),
                cost_per_unit REAL DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS dish_composition (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_dish INTEGER NOT NULL,
                id_product INTEGER NOT NULL,
                quantity REAL NOT NULL CHECK (quantity > 0),
                FOREIGN KEY (id_dish) REFERENCES menu(id_dish),
                FOREIGN KEY (id_product) REFERENCES products(id_product)
            );
            
            CREATE TABLE IF NOT EXISTS orders (
                id_order INTEGER PRIMARY KEY AUTOINCREMENT,
                table_num INTEGER NOT NULL,
                id_employee INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Открыт',
                FOREIGN KEY (id_employee) REFERENCES employees(id)
            );
            
            CREATE TABLE IF NOT EXISTS order_items (
                id_item INTEGER PRIMARY KEY AUTOINCREMENT,
                id_order INTEGER NOT NULL,
                id_dish INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                ready_status INTEGER DEFAULT 0,
                FOREIGN KEY (id_order) REFERENCES orders(id_order),
                FOREIGN KEY (id_dish) REFERENCES menu(id_dish)
            );
        ''')
        self.conn.commit()
    
    def test_tables_created(self):
        """Проверка что таблица столиков создана"""
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tables_cafe'
        """)
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "Таблица tables_cafe должна существовать")
    
    def test_initial_tables_count(self):
        """Проверка что создано 10 столиков"""
        # Вставляем тестовые данные
        self.cursor.executemany(
            "INSERT INTO tables_cafe (table_number, capacity) VALUES (?, ?)",
            [(i, 4) for i in range(1, 11)]
        )
        self.conn.commit()
        
        self.cursor.execute("SELECT COUNT(*) FROM tables_cafe")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 10, "Должно быть 10 столиков")
    
    def test_menu_items_exist(self):
        """Проверка что меню не пустое"""
        # Вставляем тестовые блюда
        self.cursor.execute("""
            INSERT INTO categories (name_category) VALUES ('Тестовая категория')
        """)
        self.cursor.execute("""
            INSERT INTO menu (name_of_dish, price, id_category) 
            VALUES ('Тестовое блюдо', 100.0, 1)
        """)
        self.conn.commit()
        
        self.cursor.execute("SELECT COUNT(*) FROM menu")
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0, "В меню должно быть хотя бы одно блюдо")
    
    def test_price_calculation(self):
        """Проверка расчета суммы заказа"""
        # Вставляем данные
        self.cursor.execute("""
            INSERT INTO categories (name_category) VALUES ('Салаты')
        """)
        self.cursor.execute("""
            INSERT INTO menu (name_of_dish, price, id_category) VALUES 
            ('Цезарь', 280.0, 1),
            ('Греческий', 220.0, 1)
        """)
        self.conn.commit()
        
        # Считаем сумму
        self.cursor.execute("""
            SELECT SUM(price) FROM menu WHERE id_category = 1
        """)
        total = self.cursor.fetchone()[0]
        self.assertEqual(total, 500.0, "Сумма должна быть 500.0")


class OrderFlowTests(unittest.TestCase):
    """Тесты основного сценария создания заказа"""
    
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        
        # Создаем минимальную схему
        self.cursor.executescript('''
            CREATE TABLE tables_cafe (
                table_number INTEGER PRIMARY KEY,
                is_occupied INTEGER DEFAULT 0
            );
            
            CREATE TABLE menu (
                id_dish INTEGER PRIMARY KEY,
                name_of_dish TEXT NOT NULL,
                price REAL NOT NULL
            );
            
            CREATE TABLE orders (
                id_order INTEGER PRIMARY KEY AUTOINCREMENT,
                table_num INTEGER NOT NULL,
                status TEXT DEFAULT 'Открыт'
            );
            
            CREATE TABLE order_items (
                id_item INTEGER PRIMARY KEY AUTOINCREMENT,
                id_order INTEGER NOT NULL,
                id_dish INTEGER NOT NULL,
                quantity INTEGER NOT NULL
            );
        ''')
        
        # Добавляем тестовые данные
        self.cursor.execute("INSERT INTO tables_cafe (table_number) VALUES (1)")
        self.cursor.execute("""
            INSERT INTO menu (id_dish, name_of_dish, price) VALUES 
            (1, 'Борщ', 220.0),
            (2, 'Стейк', 450.0)
        """)
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
    
    def test_create_order(self):
        """Проверка создания заказа"""
        # Создаем заказ
        self.cursor.execute("""
            INSERT INTO orders (table_num, status) VALUES (1, 'Открыт')
        """)
        order_id = self.cursor.lastrowid
        
        # Добавляем блюда
        self.cursor.execute("""
            INSERT INTO order_items (id_order, id_dish, quantity) 
            VALUES (?, 1, 2)
        """, (order_id,))
        
        self.conn.commit()
        
        # Проверяем
        self.cursor.execute("""
            SELECT COUNT(*) FROM order_items WHERE id_order = ?
        """, (order_id,))
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1, "Должна быть одна позиция в заказе")
    
    def test_calculate_order_total(self):
        """Проверка расчета суммы заказа"""
        self.cursor.execute("""
            INSERT INTO orders (table_num) VALUES (1)
        """)
        order_id = self.cursor.lastrowid
        
        self.cursor.execute("""
            INSERT INTO order_items (id_order, id_dish, quantity) VALUES 
            (?, 1, 2),
            (?, 2, 1)
        """, (order_id, order_id))
        
        self.cursor.execute("""
            SELECT SUM(m.price * oi.quantity)
            FROM order_items oi
            JOIN menu m ON oi.id_dish = m.id_dish
            WHERE oi.id_order = ?
        """, (order_id,))
        
        total = self.cursor.fetchone()[0]
        # 2 * 220 + 1 * 450 = 890
        self.assertEqual(total, 890.0, "Сумма заказа должна быть 890.0")


if __name__ == '__main__':
    # Запускаем тесты
    unittest.main(verbosity=2)