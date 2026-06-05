"""
Модели данных для доменной логики кафе.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Table:
    table_number: int
    capacity: int = 4
    is_occupied: bool = False


@dataclass
class Category:
    id_category: int
    name_category: str


@dataclass
class OrderItem:
    dish_id: int
    name: str
    quantity: int
    price: float

    def __post_init__(self):
        """Валидация после создания объекта"""
        from .exceptions import InvalidQuantityError, InvalidPriceError
        if self.quantity <= 0:
            raise InvalidQuantityError(
                f"Количество должно быть > 0, получено {self.quantity}"
            )
        if self.price < 0:
            raise InvalidPriceError(
                f"Цена не может быть отрицательной, получено {self.price}"
            )

    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.price, 2)


@dataclass
class Product:
    id_product: int
    name_of_product: str
    unit: str
    quantity_at_storage: float
    cost_per_unit: float = 0.0

    @property
    def total_value(self) -> float:
        return round(self.quantity_at_storage * self.cost_per_unit, 2)


@dataclass
class DishComposition:
    dish_id: int
    product_id: int
    quantity_per_portion: float


@dataclass
class Employee:
    id: int
    name: str
    surname: str
    position: str
    base_salary: float
    bonus_percent: float = 0.0

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.surname}"


@dataclass
class Order:
    id_order: int
    table_num: int
    employee_id: int
    created_at: datetime
    status: str = 'Открыт'
    items: List[OrderItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        return round(sum(item.subtotal for item in self.items), 2)