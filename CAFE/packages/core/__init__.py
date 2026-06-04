"""
Core component - переиспользуемая бизнес-логика кафе.

Этот пакет содержит:
- Модели данных
- Расчет стоимости заказов
- Управление складом
- Расчет зарплаты сотрудников

Может использоваться в:
- Tkinter приложении
- Web API (FastAPI/Flask)
- CLI утилитах
- Telegram боте
"""

from .models import (
    OrderItem,
    Product,
    DishComposition,
    Employee,
    Table,
    Order,
    Category
)
from .pricing import PricingCalculator
from .inventory import InventoryManager
from .exceptions import (
    CafeException,
    InvalidQuantityError,
    InsufficientProductsError,
    TableOccupiedError
)

__version__ = '0.1.0'
__all__ = [
    # Models
    'OrderItem',
    'Product',
    'DishComposition',
    'Employee',
    'Table',
    'Order',
    'Category',
    # Calculators
    'PricingCalculator',
    'InventoryManager',
    # Exceptions
    'CafeException',
    'InvalidQuantityError',
    'InsufficientProductsError',
    'TableOccupiedError',
]