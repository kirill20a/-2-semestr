"""
Unit tests для компонента pricing.

Проверяют:
- Расчет стоимости заказа
- Расчет зарплаты сотрудников
- Обработку ошибок
"""
import unittest
import sys
from pathlib import Path

# Добавляем путь к packages
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.pricing import PricingCalculator
from packages.core.models import OrderItem, Employee
from packages.core.exceptions import InvalidQuantityError, InvalidPriceError


class PricingCalculatorTests(unittest.TestCase):
    """Тесты для PricingCalculator"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.calculator = PricingCalculator()
    
    def test_calculate_empty_order(self):
        """Пустой заказ должен возвращать 0"""
        total = self.calculator.calculate_order_total([])
        self.assertEqual(total, 0.0)
    
    def test_calculate_single_item(self):
        """Одно блюдо в заказе"""
        items = [
            OrderItem(dish_id=1, name="Борщ", quantity=2, price=220.0)
        ]
        total = self.calculator.calculate_order_total(items)
        self.assertEqual(total, 440.0)
    
    def test_calculate_multiple_items(self):
        """Несколько блюд в заказе"""
        items = [
            OrderItem(dish_id=1, name="Борщ", quantity=1, price=220.0),
            OrderItem(dish_id=2, name="Стейк", quantity=2, price=450.0),
            OrderItem(dish_id=3, name="Салат", quantity=1, price=180.0),
        ]
        total = self.calculator.calculate_order_total(items)
        # 220 + 900 + 180 = 1300
        self.assertEqual(total, 1300.0)
    
    def test_calculate_with_zero_quantity(self):
        """Блюдо с нулевым количеством"""
        items = [
            OrderItem(dish_id=1, name="Борщ", quantity=0, price=220.0)
        ]
        with self.assertRaises(InvalidQuantityError):
            self.calculator.calculate_order_total(items)
    
    def test_calculate_with_negative_quantity(self):
        """Блюдо с отрицательным количеством"""
        items = [
            OrderItem(dish_id=1, name="Борщ", quantity=-1, price=220.0)
        ]
        with self.assertRaises(InvalidQuantityError) as context:
            self.calculator.calculate_order_total(items)
        self.assertIn("Количество должно быть", str(context.exception))
    
    def test_calculate_with_negative_price(self):
        """Блюдо с отрицательной ценой"""
        items = [
            OrderItem(dish_id=1, name="Борщ", quantity=1, price=-100.0)
        ]
        with self.assertRaises(InvalidPriceError) as context:
            self.calculator.calculate_order_total(items)
        self.assertIn("Цена не может быть отрицательной", str(context.exception))
    
    def test_calculate_item_subtotal(self):
        """Расчет стоимости позиции"""
        subtotal = self.calculator.calculate_item_subtotal(price=220.0, quantity=3)
        self.assertEqual(subtotal, 660.0)
    
    def test_employee_salary_without_bonus(self):
        """Зарплата без премии"""
        employee = Employee(
            id=1,
            name="Иван",
            surname="Иванов",
            position="Официант",
            base_salary=25000,
            bonus_percent=0
        )
        
        result = self.calculator.calculate_employee_salary(
            employee=employee,
            revenue_base=100000,
            month="2026-06"
        )
        
        self.assertEqual(result['base_salary'], 25000)
        self.assertEqual(result['bonus'], 0)
        self.assertEqual(result['total'], 25000)
        self.assertEqual(result['month'], "2026-06")
    
    def test_employee_salary_with_bonus(self):
        """Зарплата с премией"""
        employee = Employee(
            id=1,
            name="Иван",
            surname="Иванов",
            position="Официант",
            base_salary=25000,
            bonus_percent=5
        )
        
        result = self.calculator.calculate_employee_salary(
            employee=employee,
            revenue_base=100000,
            month="2026-06"
        )
        
        self.assertEqual(result['base_salary'], 25000)
        self.assertEqual(result['bonus'], 5000)  # 5% от 100000
        self.assertEqual(result['total'], 30000)
    
    def test_employee_salary_calculation_details(self):
        """Проверка всех полей в расчете зарплаты"""
        employee = Employee(
            id=2,
            name="Анна",
            surname="Петрова",
            position="Бариста",
            base_salary=30000,
            bonus_percent=3
        )
        
        result = self.calculator.calculate_employee_salary(
            employee=employee,
            revenue_base=150000,
            month="2026-07"
        )
        
        self.assertEqual(result['employee_id'], 2)
        self.assertEqual(result['name'], "Анна Петрова")
        self.assertEqual(result['position'], "Бариста")
        self.assertEqual(result['base_salary'], 30000)
        self.assertEqual(result['bonus_percent'], 3)
        self.assertEqual(result['revenue_base'], 150000)
        self.assertEqual(result['bonus'], 4500)  # 3% от 150000
        self.assertEqual(result['total'], 34500)
        self.assertEqual(result['month'], "2026-07")
    
    def test_waiter_bonus_calculation(self):
        """Расчет премии официанта от личной выручки"""
        bonus = self.calculator.calculate_waiter_bonus(
            personal_revenue=50000,
            bonus_percent=5
        )
        self.assertEqual(bonus, 2500)
    
    def test_shared_bonus_calculation(self):
        """Расчет общей премии для нескольких сотрудников"""
        bonus = self.calculator.calculate_shared_bonus(
            total_revenue=300000,
            bonus_percent=2,
            employee_count=3
        )
        # 300000 / 3 = 100000 на каждого
        # 100000 * 2% = 2000
        self.assertEqual(bonus, 2000)
    
    def test_shared_bonus_zero_employees(self):
        """Расчет премии при нулевом количестве сотрудников"""
        bonus = self.calculator.calculate_shared_bonus(
            total_revenue=100000,
            bonus_percent=5,
            employee_count=0
        )
        self.assertEqual(bonus, 0.0)


class OrderItemTests(unittest.TestCase):
    """Тесты для модели OrderItem"""
    
    def test_order_item_subtotal(self):
        """Расчет стоимости позиции"""
        item = OrderItem(dish_id=1, name="Борщ", quantity=2, price=220.0)
        self.assertEqual(item.subtotal, 440.0)
    
    def test_order_item_creation_validation(self):
        """Валидация при создании"""
        with self.assertRaises(InvalidQuantityError):
            OrderItem(dish_id=1, name="Борщ", quantity=0, price=220.0)
        
        with self.assertRaises(InvalidPriceError):
            OrderItem(dish_id=1, name="Борщ", quantity=1, price=-100.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)