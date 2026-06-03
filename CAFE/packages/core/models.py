"""
Модели данных для доменной логики кафе.

Используем dataclasses для чистоты и типизации.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Table:
    """Столик в кафе"""
    table_number: int
    capacity: int = 4
    is_occupied: bool = False
    
    def occupy(self):
        """Занять столик"""
        if self.is_occupied:
            from .exceptions import TableOccupiedError
            raise TableOccupiedError(f"Столик {self.table_number} уже занят")
        self.is_occupied = True
    
    def free(self):
        """Освободить столик"""
        self.is_occupied = False


@dataclass
class Category:
    """Категория блюда"""
    id_category: int
    name_category: str


@dataclass
class OrderItem:
    """Позиция в заказе"""
    dish_id: int
    name: str
    quantity: int
    price: float
    
    @property
    def subtotal(self) -> float:
        """Стоимость позиции"""
        return round(self.quantity * self.price, 2)
    
    def __post_init__(self):
        """Валидация после инициализации"""
        from .exceptions import InvalidQuantityError, InvalidPriceError
        if self.quantity <= 0:
            raise InvalidQuantityError(f"Количество должно быть > 0, получено {self.quantity}")
        if self.price < 0:
            raise InvalidPriceError(f"Цена не может быть отрицательной, получено {self.price}")


@dataclass
class Product:
    """Продукт на складе"""
    id_product: int
    name_of_product: str
    unit: str  # кг, л, шт и т.д.
    quantity_at_storage: float
    cost_per_unit: float = 0.0
    
    @property
    def total_value(self) -> float:
        """Общая стоимость продукта на складе"""
        return round(self.quantity_at_storage * self.cost_per_unit, 2)
    
    def check_availability(self, needed: float) -> bool:
        """Проверить хватает ли продукта"""
        return self.quantity_at_storage >= needed
    
    def deduct(self, amount: float):
        """Списать продукт"""
        from .exceptions import InsufficientProductsError
        if not self.check_availability(amount):
            raise InsufficientProductsError([
                f"{self.name_of_product}: есть {self.quantity_at_storage}, нужно {amount}"
            ])
        self.quantity_at_storage -= amount


@dataclass
class DishComposition:
    """Состав блюда (техкарта)"""
    dish_id: int
    product_id: int
    quantity_per_portion: float  # Сколько продукта нужно на одну порцию


@dataclass
class Employee:
    """Сотрудник кафе"""
    id: int
    name: str
    surname: str
    position: str
    base_salary: float
    bonus_percent: float = 0.0
    
    @property
    def full_name(self) -> str:
        """Полное имя"""
        return f"{self.name} {self.surname}"


@dataclass
class Order:
    """Заказ"""
    id_order: int
    table_num: int
    employee_id: int
    created_at: datetime
    status: str = 'Открыт'  # Открыт, Готовится, Выполнен, Оплачен
    items: List[OrderItem] = field(default_factory=list)
    
    @property
    def total(self) -> float:
        """Общая сумма заказа"""
        return round(sum(item.subtotal for item in self.items), 2)
    
    def add_item(self, item: OrderItem):
        """Добавить позицию в заказ"""
        self.items.append(item)