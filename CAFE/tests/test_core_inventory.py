"""
Unit tests для компонента inventory.

Проверяют:
- Проверку наличия продуктов
- Списание продуктов
- Пополнение склада
"""
import unittest
import sys
from pathlib import Path

# Добавляем путь к packages
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.inventory import InventoryManager
from packages.core.models import Product, DishComposition
from packages.core.exceptions import InsufficientProductsError


class InventoryManagerTests(unittest.TestCase):
    """Тесты для InventoryManager"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.products = {
            1: Product(
                id_product=1,
                name_of_product="Куриное филе",
                unit="кг",
                quantity_at_storage=5.0,
                cost_per_unit=280.0
            ),
            2: Product(
                id_product=2,
                name_of_product="Говядина",
                unit="кг",
                quantity_at_storage=3.0,
                cost_per_unit=600.0
            ),
            3: Product(
                id_product=3,
                name_of_product="Салат Айсберг",
                unit="кг",
                quantity_at_storage=2.0,
                cost_per_unit=350.0
            ),
        }
        self.manager = InventoryManager(self.products)
    
    def test_get_product(self):
        """Получение продукта по ID"""
        product = self.manager.get_product(1)
        self.assertEqual(product.name_of_product, "Куриное филе")
        self.assertEqual(product.quantity_at_storage, 5.0)
    
    def test_get_nonexistent_product(self):
        """Получение несуществующего продукта"""
        with self.assertRaises(ValueError) as context:
            self.manager.get_product(999)
        self.assertIn("не найден", str(context.exception))
    
    def test_check_availability_enough(self):
        """Проверка наличия - продуктов хватает"""
        compositions = [
            DishComposition(dish_id=1, product_id=1, quantity_per_portion=0.150),
        ]
        quantities = {1: 2}  # 2 порции = 0.3 кг, есть 5 кг
        
        shortages = self.manager.check_availability(compositions, quantities)
        self.assertEqual(len(shortages), 0)
    
    def test_check_availability_shortage(self):
        """Проверка наличия - продуктов не хватает"""
        compositions = [
            DishComposition(dish_id=1, product_id=1, quantity_per_portion=3.0),
        ]
        quantities = {1: 2}  # Нужно 6 кг, есть только 5
        
        shortages = self.manager.check_availability(compositions, quantities)
        self.assertEqual(len(shortages), 1)
        self.assertIn("Куриное филе", shortages[0])
        self.assertIn("5.000", shortages[0])
        self.assertIn("6.000", shortages[0])
    
    def test_check_availability_multiple_products(self):
        """Проверка наличия нескольких продуктов"""
        compositions = [
            DishComposition(dish_id=1, product_id=1, quantity_per_portion=2.0),
            DishComposition(dish_id=1, product_id=3, quantity_per_portion=1.0),
        ]
        quantities = {1: 2}  # Нужно 4 кг курицы и 2 кг салата
        
        shortages = self.manager.check_availability(compositions, quantities)
        # Курицы нужно 4 кг (есть 5) - OK
        # Салата нужно 2 кг (есть 2) - OK
        self.assertEqual(len(shortages), 0)
    
    def test_has_sufficient_products_true(self):
        """Проверка хватает ли продуктов - True"""
        compositions = [
            DishComposition(dish_id=1, product_id=1, quantity_per_portion=1.0),
        ]
        quantities = {1: 3}  # Нужно 3 кг, есть 5
        
        result = self.manager.has_sufficient_products(compositions, quantities)
        self.assertTrue(result)
    
    def test_has_sufficient_products_false(self):
        """Проверка хватает ли продуктов - False"""
        compositions = [
            DishComposition(dish_id=1, product_id=1, quantity_per_portion=3.0),
        ]
        quantities = {1: 2}  # Нужно 6 кг, есть 5
        
        result = self.manager.has_sufficient_products(compositions, quantities)
        self.assertFalse(result)
    
    def test_deduct_products_success(self):
        """Успешное списание продуктов"""
        compositions = [
            DishComposition(dish_id=1, product_id=1, quantity_per_portion=0.150),
        ]
        quantities = {1: 2}  # 2 порции = 0.3 кг
        
        updated = self.manager.deduct_products(compositions, quantities)
        
        self.assertIn(1, updated)
        self.assertEqual(updated[1], 4.7)  # 5.0 - 0.3
        
        # Проверяем что продукт действительно списался
        product = self.manager.get_product(1)
        self.assertEqual(product.quantity_at_storage, 4.7)
    
    def test_deduct_products_insufficient(self):
        """Списание при недостатке продуктов"""
        compositions = [
            DishComposition(dish_id=1, product_id=1, quantity_per_portion=3.0),
        ]
        quantities = {1: 2}  # Нужно 6 кг, есть 5
        
        with self.assertRaises(InsufficientProductsError) as context:
            self.manager.deduct_products(compositions, quantities)
        
        self.assertIn("Куриное филе", str(context.exception))
    
    def test_restock_product(self):
        """Пополнение склада"""
        initial_qty = self.manager.get_product(1).quantity_at_storage
        
        self.manager.restock_product(1, 2.0)
        
        product = self.manager.get_product(1)
        self.assertEqual(product.quantity_at_storage, initial_qty + 2.0)
    
    def test_restock_negative_amount(self):
        """Пополнение отрицательным количеством"""
        with self.assertRaises(ValueError) as context:
            self.manager.restock_product(1, -1.0)
        self.assertIn("должно быть > 0", str(context.exception))
    
    def test_get_low_stock_products(self):
        """Получение продуктов с низким остатком"""
        # Добавляем продукт с низким остатком
        self.products[4] = Product(
            id_product=4,
            name_of_product="Лимоны",
            unit="кг",
            quantity_at_storage=0.5,
            cost_per_unit=180.0
        )
        
        manager = InventoryManager(self.products)
        low_stock = manager.get_low_stock_products(threshold=1.0)
        
        self.assertEqual(len(low_stock), 1)
        self.assertEqual(low_stock[0].name_of_product, "Лимоны")
    
    def test_get_total_inventory_value(self):
        """Расчет общей стоимости склада"""
        # 5 * 280 + 3 * 600 + 2 * 350 = 1400 + 1800 + 700 = 3900
        total = self.manager.get_total_inventory_value()
        self.assertEqual(total, 3900.0)


class DishCompositionTests(unittest.TestCase):
    """Тесты для модели DishComposition"""
    
    def test_dish_composition_creation(self):
        """Создание техкарты"""
        composition = DishComposition(
            dish_id=1,
            product_id=2,
            quantity_per_portion=0.300
        )
        
        self.assertEqual(composition.dish_id, 1)
        self.assertEqual(composition.product_id, 2)
        self.assertEqual(composition.quantity_per_portion, 0.300)


if __name__ == '__main__':
    unittest.main(verbosity=2)