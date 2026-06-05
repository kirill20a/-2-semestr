"""Тесты моделей данных"""
import unittest
from src.models import Dish, Employee, Order


class TestModels(unittest.TestCase):
    
    def test_dish_creation(self):
        dish = Dish(id=1, name="Цезарь", price=280.0, 
                    category_id=1, cooking_time=10)
        self.assertEqual(dish.name, "Цезарь")
        self.assertEqual(dish.price, 280.0)
        self.assertTrue(dish.is_available)
    
    def test_employee_full_name(self):
        emp = Employee(id=1, name="Иван", surname="Иванов", position_id=2)
        self.assertEqual(emp.full_name, "Иван Иванов")
    
    def test_order_defaults(self):
        order = Order()
        self.assertEqual(order.status, "Открыт")


if __name__ == '__main__':
    unittest.main()