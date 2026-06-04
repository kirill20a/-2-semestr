"""Модели данных"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Dish:
    id: int
    name: str
    price: float
    category_id: int
    cooking_time: int
    is_available: bool = True


@dataclass
class Product:
    id: int
    name: str
    unit: str
    quantity: float
    cost_per_unit: float


@dataclass
class Employee:
    id: int
    name: str
    surname: str
    position_id: int

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"


@dataclass
class Order:
    id: Optional[int] = None
    table_num: int = 0
    employee_id: int = 0
    status: str = "Открыт"