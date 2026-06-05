"""
Кастомные исключения для бизнес-логики кафе.
"""


class CafeException(Exception):
    """Базовое исключение для всех ошибок кафе"""
    pass


class InvalidQuantityError(CafeException):
    """Ошибка неверного количества (отрицательное или ноль)"""
    pass


class InvalidPriceError(CafeException):
    """Ошибка неверной цены (отрицательная)"""
    pass


class InsufficientProductsError(CafeException):
    """Ошибка недостаточного количества продуктов на складе"""
    def __init__(self, shortages: list):
        self.shortages = shortages
        message = "Недостаточно продуктов на складе:\n" + "\n".join(shortages)
        super().__init__(message)


class TableOccupiedError(CafeException):
    """Ошибка попытки занять уже занятый столик"""
    pass


class TableNotFoundError(CafeException):
    """Ошибка когда столик не найден"""
    pass


class DishNotFoundError(CafeException):
    """Ошибка когда блюдо не найдено в меню"""
    pass


class EmployeeNotFoundError(CafeException):
    """Ошибка когда сотрудник не найден"""
    pass