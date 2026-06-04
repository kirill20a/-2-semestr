"""
Компонент для расчетов:
- Стоимость заказов
- Зарплата сотрудников
- Выручка
"""
from typing import List, Dict
from .models import OrderItem, Employee


class PricingCalculator:
    """Калькулятор стоимости и зарплаты"""
    
    @staticmethod
    def calculate_order_total(items: List[OrderItem]) -> float:
        """
        Расчет общей суммы заказа.
        
        Args:
            items: Список позиций заказа
            
        Returns:
            Общая сумма заказа
            
        Raises:
            InvalidQuantityError: если количество <= 0
            InvalidPriceError: если цена < 0
        """
        if not items:
            return 0.0
        
        total = 0.0
        for item in items:
            # Валидация происходит в __post_init__ OrderItem
            total += item.subtotal
        
        return round(total, 2)
    
    @staticmethod
    def calculate_item_subtotal(price: float, quantity: int) -> float:
        """
        Расчет стоимости одной позиции.
        
        Args:
            price: Цена блюда
            quantity: Количество
            
        Returns:
            Стоимость позиции
        """
        from .exceptions import InvalidQuantityError, InvalidPriceError
        
        if quantity <= 0:
            raise InvalidQuantityError(f"Количество должно быть > 0, получено {quantity}")
        if price < 0:
            raise InvalidPriceError(f"Цена не может быть отрицательной, получено {price}")
        
        return round(price * quantity, 2)
    
    @staticmethod
    def calculate_employee_salary(
        employee: Employee,
        revenue_base: float,
        month: str
    ) -> Dict:
        """
        Расчет зарплаты сотрудника с премией.
        
        Args:
            employee: Данные сотрудника
            revenue_base: База для расчета премии (выручка)
            month: Месяц в формате YYYY-MM
            
        Returns:
            Словарь с расчетом:
            {
                'employee_id': int,
                'name': str,
                'position': str,
                'base_salary': float,
                'bonus_percent': float,
                'revenue_base': float,
                'bonus': float,
                'total': float,
                'month': str
            }
        """
        bonus = revenue_base * employee.bonus_percent / 100
        total = employee.base_salary + bonus
        
        return {
            'employee_id': employee.id,
            'name': employee.full_name,
            'position': employee.position,
            'base_salary': employee.base_salary,
            'bonus_percent': employee.bonus_percent,
            'revenue_base': round(revenue_base, 2),
            'bonus': round(bonus, 2),
            'total': round(total, 2),
            'month': month
        }
    
    @staticmethod
    def calculate_waiter_bonus(
        personal_revenue: float,
        bonus_percent: float
    ) -> float:
        """
        Расчет премии официанта от личной выручки.
        
        Args:
            personal_revenue: Личная выручка официанта
            bonus_percent: Процент премии
            
        Returns:
            Сумма премии
        """
        return round(personal_revenue * bonus_percent / 100, 2)
    
    @staticmethod
    def calculate_shared_bonus(
        total_revenue: float,
        bonus_percent: float,
        employee_count: int
    ) -> float:
        """
        Расчет премии для сотрудников с общей базой.
        
        Args:
            total_revenue: Общая выручка (бара, кухни или всего кафе)
            bonus_percent: Процент премии
            employee_count: Количество сотрудников для разделения
            
        Returns:
            Премия на одного сотрудника
        """
        if employee_count <= 0:
            return 0.0
        
        revenue_per_employee = total_revenue / employee_count
        bonus = revenue_per_employee * bonus_percent / 100
        
        return round(bonus, 2)