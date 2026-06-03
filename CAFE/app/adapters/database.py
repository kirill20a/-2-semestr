"""
Адаптер для работы с базой данных.

Отделяет инфраструктуру (SQLite) от бизнес-логики.
Преобразует данные между БД и domain-моделями.
"""
import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

# Импортируем модели из core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.core.models import (
    OrderItem, Product, DishComposition, 
    Employee, Table, Category, Order
)
from app.config import config


class DatabaseAdapter:
    """Адаптер для работы с SQLite базой данных"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Инициализация адаптера.
        
        Args:
            db_path: Путь к базе данных (по умолчанию из config)
        """
        self.db_path = db_path or str(config.DB_PATH)
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Cursor:
        """
        Подключение к БД.
        
        Returns:
            Cursor для выполнения запросов
        """
        # Создаем директорию если нет
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Для доступа по имени колонок
        return self.conn.cursor()
    
    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    # ========== Tables ==========
    
    def get_all_tables(self) -> List[Table]:
        """Получить все столики"""
        cursor = self.connect()
        cursor.execute("""
            SELECT table_number, capacity, is_occupied 
            FROM tables_cafe 
            ORDER BY table_number
        """)
        
        tables = [
            Table(
                table_number=row['table_number'],
                capacity=row['capacity'],
                is_occupied=bool(row['is_occupied'])
            )
            for row in cursor.fetchall()
        ]
        self.close()
        return tables
    
    def get_free_tables(self) -> List[Table]:
        """Получить свободные столики"""
        cursor = self.connect()
        cursor.execute("""
            SELECT table_number, capacity, is_occupied 
            FROM tables_cafe 
            WHERE is_occupied = 0
            ORDER BY table_number
        """)
        
        tables = [
            Table(
                table_number=row['table_number'],
                capacity=row['capacity'],
                is_occupied=False
            )
            for row in cursor.fetchall()
        ]
        self.close()
        return tables
    
    def occupy_table(self, table_number: int):
        """Занять столик"""
        cursor = self.connect()
        cursor.execute("""
            UPDATE tables_cafe 
            SET is_occupied = 1 
            WHERE table_number = ?
        """, (table_number,))
        self.conn.commit()
        self.close()
    
    def free_table(self, table_number: int):
        """Освободить столик"""
        cursor = self.connect()
        cursor.execute("""
            UPDATE tables_cafe 
            SET is_occupied = 0 
            WHERE table_number = ?
        """, (table_number,))
        self.conn.commit()
        self.close()
    
    # ========== Menu & Categories ==========
    
    def get_all_categories(self) -> List[Category]:
        """Получить все категории"""
        cursor = self.connect()
        cursor.execute("""
            SELECT id_category, name_category 
            FROM categories 
            ORDER BY name_category
        """)
        
        categories = [
            Category(
                id_category=row['id_category'],
                name_category=row['name_category']
            )
            for row in cursor.fetchall()
        ]
        self.close()
        return categories
    
    def get_menu_items(self, available_only: bool = True) -> List[Dict]:
        """
        Получить меню с категориями.
        
        Returns:
            Список словарей с информацией о блюдах
        """
        cursor = self.connect()
        
        query = """
            SELECT m.id_dish, m.name_of_dish, m.price, 
                   m.cooking_time, m.is_available,
                   c.name_category
            FROM menu m
            JOIN categories c ON m.id_category = c.id_category
        """
        
        if available_only:
            query += " WHERE m.is_available = 1"
        
        query += " ORDER BY c.name_category, m.name_of_dish"
        
        items = [dict(row) for row in cursor.fetchall()]
        self.close()
        return items
    
    # ========== Employees ==========
    
    def get_waiters(self) -> List[Employee]:
        """Получить список официантов"""
        cursor = self.connect()
        cursor.execute("""
            SELECT e.id, e.name, e.surname, j.name as position,
                   j.salary_base, j.bonus_percent
            FROM employees e
            JOIN job_titles j ON e.id_job_title = j.id
            WHERE j.name = 'Официант'
            ORDER BY e.name
        """)
        
        employees = [
            Employee(
                id=row['id'],
                name=row['name'],
                surname=row['surname'],
                position=row['position'],
                base_salary=row['salary_base'],
                bonus_percent=row['bonus_percent']
            )
            for row in cursor.fetchall()
        ]
        self.close()
        return employees
    
    def get_all_employees(self) -> List[Employee]:
        """Получить всех сотрудников"""
        cursor = self.connect()
        cursor.execute("""
            SELECT e.id, e.name, e.surname, j.name as position,
                   j.salary_base, j.bonus_percent
            FROM employees e
            JOIN job_titles j ON e.id_job_title = j.id
            ORDER BY j.name, e.name
        """)
        
        employees = [
            Employee(
                id=row['id'],
                name=row['name'],
                surname=row['surname'],
                position=row['position'],
                base_salary=row['salary_base'],
                bonus_percent=row['bonus_percent']
            )
            for row in cursor.fetchall()
        ]
        self.close()
        return employees
    
    # ========== Products & Inventory ==========
    
    def get_all_products(self) -> Dict[int, Product]:
        """
        Получить все продукты.
        
        Returns:
            Словарь {id_product: Product}
        """
        cursor = self.connect()
        cursor.execute("""
            SELECT id_product, name_of_product, unit, 
                   quantity_at_storage, cost_per_unit
            FROM products
            ORDER BY name_of_product
        """)
        
        products = {
            row['id_product']: Product(
                id_product=row['id_product'],
                name_of_product=row['name_of_product'],
                unit=row['unit'],
                quantity_at_storage=row['quantity_at_storage'],
                cost_per_unit=row['cost_per_unit']
            )
            for row in cursor.fetchall()
        }
        self.close()
        return products
    
    def get_dish_compositions(self, dish_id: Optional[int] = None) -> List[DishComposition]:
        """
        Получить техкарты блюд.
        
        Args:
            dish_id: ID блюда (None для всех)
            
        Returns:
            Список DishComposition
        """
        cursor = self.connect()
        
        if dish_id:
            cursor.execute("""
                SELECT id_dish, id_product, quantity
                FROM dish_composition
                WHERE id_dish = ?
            """, (dish_id,))
        else:
            cursor.execute("""
                SELECT id_dish, id_product, quantity
                FROM dish_composition
            """)
        
        compositions = [
            DishComposition(
                dish_id=row['id_dish'],
                product_id=row['id_product'],
                quantity_per_portion=row['quantity']
            )
            for row in cursor.fetchall()
        ]
        self.close()
        return compositions
    
    def update_product_quantity(self, product_id: int, new_quantity: float):
        """Обновить количество продукта"""
        cursor = self.connect()
        cursor.execute("""
            UPDATE products 
            SET quantity_at_storage = ? 
            WHERE id_product = ?
        """, (new_quantity, product_id))
        self.conn.commit()
        self.close()
    
    # ========== Orders ==========
    
    def create_order(self, table_num: int, employee_id: int) -> int:
        """
        Создать новый заказ.
        
        Returns:
            ID созданного заказа
        """
        cursor = self.connect()
        cursor.execute("""
            INSERT INTO orders (table_num, id_employee, created_at, status)
            VALUES (?, ?, ?, 'Готовится')
        """, (table_num, employee_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        order_id = cursor.lastrowid
        self.conn.commit()
        self.close()
        return order_id
    
    def add_order_item(self, order_id: int, dish_id: int, quantity: int):
        """Добавить позицию в заказ"""
        cursor = self.connect()
        cursor.execute("""
            INSERT INTO order_items (id_order, id_dish, quantity, ready_status)
            VALUES (?, ?, ?, 0)
        """, (order_id, dish_id, quantity))
        self.conn.commit()
        self.close()
    
    def get_order_items(self, order_id: int) -> List[OrderItem]:
        """Получить позиции заказа"""
        cursor = self.connect()
        cursor.execute("""
            SELECT m.id_dish, m.name_of_dish, oi.quantity, m.price
            FROM order_items oi
            JOIN menu m ON oi.id_dish = m.id_dish
            WHERE oi.id_order = ?
        """, (order_id,))
        
        items = [
            OrderItem(
                dish_id=row['id_dish'],
                name=row['name_of_dish'],
                quantity=row['quantity'],
                price=row['price']
            )
            for row in cursor.fetchall()
        ]
        self.close()
        return items
    
    def get_order_revenue(self, date_from: str, date_to: str) -> float:
        """
        Получить выручку за период.
        
        Args:
            date_from: Начальная дата (YYYY-MM-DD)
            date_to: Конечная дата (YYYY-MM-DD)
            
        Returns:
            Сумма выручки
        """
        cursor = self.connect()
        cursor.execute("""
            SELECT COALESCE(SUM(m.price * oi.quantity), 0) as revenue
            FROM orders o
            JOIN order_items oi ON o.id_order = oi.id_order
            JOIN menu m ON oi.id_dish = m.id_dish
            WHERE DATE(o.created_at) BETWEEN ? AND ?
              AND o.status IN ('Оплачен', 'Выполнен')
        """, (date_from, date_to))
        
        revenue = cursor.fetchone()[0]
        self.close()
        return revenue