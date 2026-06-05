"""
Компонент управления складом:
- Проверка наличия продуктов
- Списание по техкартам
- Пополнение склада
"""
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import OrderItem, Employee

from .exceptions import InsufficientProductsError


class InventoryManager:
    """Управление складом и техкартами"""
    
    def __init__(self, products: Dict[int, Product]):
        """
        Инициализация менеджера склада.
        
        Args:
            products: Словарь продуктов {id_product: Product}
        """
        self.products = products.copy()  # Копия чтобы не менять оригинал
    
    def get_product(self, product_id: int) -> Product:
        """Получить продукт по ID"""
        if product_id not in self.products:
            raise ValueError(f"Продукт с ID {product_id} не найден")
        return self.products[product_id]
    
    def check_availability(
        self,
        dish_compositions: List[DishComposition],
        order_quantities: Dict[int, int]  # dish_id -> quantity
    ) -> List[str]:
        """
        Проверка наличия продуктов для заказа.
        
        Args:
            dish_compositions: Список техкарт блюд
            order_quantities: Словарь {dish_id: количество порций}
            
        Returns:
            Список строк с недостающими продуктами.
            Пустой список если всего хватает.
        """
        shortages = []
        
        # Считаем сколько нужно каждого продукта
        needed = {}
        for composition in dish_compositions:
            dish_qty = order_quantities.get(composition.dish_id, 0)
            if dish_qty == 0:
                continue
                
            total_needed = composition.quantity_per_portion * dish_qty
            needed[composition.product_id] = needed.get(composition.product_id, 0) + total_needed
        
        # Проверяем наличие
        for prod_id, total_needed in needed.items():
            product = self.products.get(prod_id)
            if product is None:
                shortages.append(f"Продукт ID {prod_id} не найден в базе")
                continue
                
            if product.quantity_at_storage < total_needed:
                shortages.append(
                    f"{product.name_of_product}: есть {product.quantity_at_storage:.3f} {product.unit}, "
                    f"нужно {total_needed:.3f} {product.unit}"
                )
        
        return shortages
    
    def has_sufficient_products(
        self,
        dish_compositions: List[DishComposition],
        order_quantities: Dict[int, int]
    ) -> bool:
        """
        Проверка хватает ли продуктов.
        
        Returns:
            True если всего хватает, False иначе
        """
        shortages = self.check_availability(dish_compositions, order_quantities)
        return len(shortages) == 0
    
    def deduct_products(
        self,
        dish_compositions: List[DishComposition],
        order_quantities: Dict[int, int]
    ) -> Dict[int, float]:
        """
        Списание продуктов со склада.
        
        Args:
            dish_compositions: Список техкарт блюд
            order_quantities: Словарь {dish_id: количество порций}
            
        Returns:
            Словарь {product_id: новый_остаток}
            
        Raises:
            InsufficientProductsError: если продуктов не хватает
        """
        # Сначала проверяем наличие
        shortages = self.check_availability(dish_compositions, order_quantities)
        if shortages:
            raise InsufficientProductsError(shortages)
        
        updated = {}
        
        # Считаем сколько нужно списать
        to_deduct = {}
        for composition in dish_compositions:
            dish_qty = order_quantities.get(composition.dish_id, 0)
            if dish_qty == 0:
                continue
                
            amount = composition.quantity_per_portion * dish_qty
            to_deduct[composition.product_id] = to_deduct.get(composition.product_id, 0) + amount
        
        # Списываем
        for prod_id, amount in to_deduct.items():
            if prod_id in self.products:
                self.products[prod_id].quantity_at_storage -= amount
                updated[prod_id] = self.products[prod_id].quantity_at_storage
        
        return updated
    
    def restock_product(self, product_id: int, amount: float):
        """
        Пополнение склада.
        
        Args:
            product_id: ID продукта
            amount: Количество для добавления
        """
        if amount <= 0:
            raise ValueError("Количество для пополнения должно быть > 0")
        
        if product_id not in self.products:
            raise ValueError(f"Продукт с ID {product_id} не найден")
        
        self.products[product_id].quantity_at_storage += amount
    
    def get_low_stock_products(self, threshold: float = 1.0) -> List[Product]:
        """
        Получить продукты с низким остатком.
        
        Args:
            threshold: Порог ниже которого продукт считается заканчивающимся
            
        Returns:
            Список продуктов с низким остатком
        """
        return [p for p in self.products.values() if p.quantity_at_storage < threshold]
    
    def get_total_inventory_value(self) -> float:
        """
        Расчет общей стоимости товаров на складе.
        
        Returns:
            Общая стоимость
        """
        return sum(p.total_value for p in self.products.values())