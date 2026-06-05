"""
Главное окно Tkinter приложения.

Использует:
- app.adapters.database для работы с БД
- packages.core для бизнес-логики
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
import sys

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.adapters.database import DatabaseAdapter
from packages.core.pricing import PricingCalculator
from packages.core.inventory import InventoryManager
from packages.core.models import OrderItem


class CafeApp:
    """Основное приложение кафе"""
    
    def __init__(self, root):
        """
        Инициализация приложения.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Кафе: Система обслуживания")
        self.root.geometry("750x650")
        self.root.configure(bg='#f0f0f0')
        
        # Инициализация компонентов
        self.db = DatabaseAdapter()
        self.pricing = PricingCalculator()
        
        # Состояние приложения
        self.cart: list = []  # Текущий заказ: список OrderItem
        self.current_table: int = 1
        self.current_waiter_id: int = 1
        
        # Построение интерфейса
        self.build_widgets()
        self.load_initial_data()
    
    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.load_free_tables()
        self.load_waiters()
        self.load_menu()
    
    def build_widgets(self):
        """Построение интерфейса"""
        # ===== ШАПКА =====
        header = tk.Frame(self.root, bg='#4a7c59', height=60)
        header.pack(fill='x')
        tk.Label(header, text="🍽️  КАФЕ «ВКУСНОЕ МЕСТО»", 
                 font=('Arial', 16, 'bold'), 
                 bg='#4a7c59', fg='white').pack(pady=12)
        
        # ===== ВЫБОР СТОЛИКА =====
        self._build_table_selection()
        
        # ===== ВЫБОР БЛЮДА =====
        self._build_dish_selection()
        
        # ===== КОРЗИНА =====
        self._build_cart()
        
        # ===== КНОПКИ ДЕЙСТВИЙ =====
        self._build_action_buttons()
    
    def _build_table_selection(self):
        """Построение секции выбора столика"""
        table_frame = tk.Frame(self.root, bg='#f0f0f0')
        table_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Label(table_frame, text="Столик №:", 
                 font=('Arial', 11), bg='#f0f0f0').pack(side='left')
        
        self.table_combo = ttk.Combobox(table_frame, state="readonly", 
                                         width=5, font=('Arial', 12))
        self.table_combo.pack(side='left', padx=5)
        
        tk.Label(table_frame, text="Официант:", 
                 font=('Arial', 11), bg='#f0f0f0').pack(side='left', padx=(20, 5))
        
        self.waiter_combo = ttk.Combobox(table_frame, state="readonly", 
                                          width=30)
        self.waiter_combo.pack(side='left', padx=5)
        
        ttk.Button(table_frame, text="🆕 Новый заказ", 
                   command=self.new_order).pack(side='right', padx=10)
    
    def _build_dish_selection(self):
        """Построение секции выбора блюда"""
        dish_frame = tk.LabelFrame(self.root, text="📋 Меню", 
                                    font=('Arial', 11, 'bold'), 
                                    bg='#f0f0f0', fg='#333')
        dish_frame.pack(fill='x', padx=15, pady=5)
        
        inner_frame = tk.Frame(dish_frame, bg='#f0f0f0')
        inner_frame.pack(padx=10, pady=10)
        
        tk.Label(inner_frame, text="Блюдо:", 
                 font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=0)
        
        self.dish_combo = ttk.Combobox(inner_frame, state="readonly", 
                                        width=40)
        self.dish_combo.grid(row=0, column=1, padx=5)
        
        tk.Label(inner_frame, text="Кол-во:", 
                 font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=2, padx=(10, 0))
        
        self.qty_entry = ttk.Entry(inner_frame, width=6, font=('Arial', 11))
        self.qty_entry.grid(row=0, column=3, padx=5)
        self.qty_entry.insert(0, "1")
        
        ttk.Button(inner_frame, text="➕ Добавить", 
                   command=self.add_to_cart).grid(row=0, column=4, padx=15)
    
    def _build_cart(self):
        """Построение секции корзины"""
        cart_frame = tk.LabelFrame(self.root, text="🧾 Текущий заказ", 
                                    font=('Arial', 11, 'bold'), 
                                    bg='#f0f0f0', fg='#333')
        cart_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        self.cart_listbox = tk.Listbox(cart_frame, width=80, height=10, 
                                        font=('Consolas', 10))
        self.cart_listbox.pack(side='left', fill='both', expand=True, 
                               padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(cart_frame, command=self.cart_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.cart_listbox.config(yscrollcommand=scrollbar.set)
    
    def _build_action_buttons(self):
        """Построение кнопок действий"""
        action_frame = tk.Frame(self.root, bg='#f0f0f0')
        action_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Button(action_frame, text="💰 Оплатить", 
                   command=self.checkout).pack(side='left', padx=5)
        
        ttk.Button(action_frame, text="🆓 Освободить столик", 
                   command=self.free_table).pack(side='left', padx=5)
        
        ttk.Button(action_frame, text="❌ Отменить", 
                   command=self.cancel_order).pack(side='left', padx=5)
    
    # ========== Data Loading ==========
    
    def load_free_tables(self):
        """Загрузка свободных столиков"""
        tables = self.db.get_free_tables()
        table_numbers = [str(t.table_number) for t in tables]
        
        self.table_combo['values'] = table_numbers
        if table_numbers:
            self.table_combo.set(table_numbers[0])
            self.current_table = int(table_numbers[0])
    
    def load_waiters(self):
        """Загрузка официантов"""
        waiters = self.db.get_waiters()
        waiter_names = [f"{w.name} {w.surname}" for w in waiters]
        
        self.waiter_combo['values'] = waiter_names
        if waiter_names:
            self.waiter_combo.set(waiter_names[0])
            # Находим ID первого официанта
            self.current_waiter_id = waiters[0].id
    
    def load_menu(self):
        """Загрузка меню"""
        menu_items = self.db.get_menu_items()
        dish_names = [item['name_of_dish'] for item in menu_items]
        
        # Сохраняем меню для быстрого доступа
        self.menu_dict = {item['name_of_dish']: item for item in menu_items}
        
        self.dish_combo['values'] = dish_names
        if dish_names:
            self.dish_combo.set(dish_names[0])
    
    # ========== Cart Operations ==========
    
    def new_order(self):
        """Новый заказ"""
        if self.cart and not messagebox.askyesno("Новый заказ", 
                "Текущий заказ будет потерян. Продолжить?"):
            return
        
        self.cart = []
        self.refresh_cart_display()
    
    def add_to_cart(self):
        """Добавить блюдо в корзину"""
        dish_name = self.dish_combo.get()
        if not dish_name:
            messagebox.showwarning("Внимание", "Выберите блюдо из меню")
            return
        
        try:
            qty = int(self.qty_entry.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", 
                "Количество должно быть целым положительным числом")
            return
        
        # Получаем информацию о блюде
        dish_info = self.menu_dict.get(dish_name)
        if not dish_info:
            messagebox.showerror("Ошибка", "Блюдо не найдено")
            return
        
        # Создаем OrderItem
        order_item = OrderItem(
            dish_id=dish_info['id_dish'],
            name=dish_info['name_of_dish'],
            quantity=qty,
            price=dish_info['price']
        )
        
        # Проверяем есть ли уже такое блюдо в заказе
        for item in self.cart:
            if item.dish_id == order_item.dish_id:
                # Увеличиваем количество
                item.quantity += qty
                self.refresh_cart_display()
                return
        
        # Добавляем новое
        self.cart.append(order_item)
        self.refresh_cart_display()
    
    def refresh_cart_display(self):
        """Обновление отображения корзины"""
        self.cart_listbox.delete(0, tk.END)
        
        # Используем PricingCalculator для расчета
        total = self.pricing.calculate_order_total(self.cart)
        
        for item in self.cart:
            subtotal = item.subtotal
            self.cart_listbox.insert(tk.END, 
                f"{item.name:35} {item.quantity:3} x {item.price:8.2f} = {subtotal:8.2f} ₽")
        
        self.cart_listbox.insert(tk.END, "─" * 65)
        self.cart_listbox.insert(tk.END, f"{'ИТОГО:':>40} {total:15.2f} ₽")
    
    def cancel_order(self):
        """Отмена заказа"""
        self.cart = []
        self.refresh_cart_display()
        messagebox.showinfo("Отмена", "Заказ отменён")
    
    def checkout(self):
        """Оплата заказа"""
        if not self.cart:
            messagebox.showwarning("Корзина пуста", "Добавьте блюда в заказ")
            return
        
        # Получаем номер столика
        try:
            table_num = int(self.table_combo.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Выберите столик")
            return
        
        # Получаем официанта
        waiter_name = self.waiter_combo.get()
        waiters = self.db.get_waiters()
        waiter = next((w for w in waiters if f"{w.name} {w.surname}" == waiter_name), None)
        
        if not waiter:
            messagebox.showerror("Ошибка", "Официант не найден")
            return
        
        # Проверяем наличие продуктов
        products = self.db.get_all_products()
        all_compositions = self.db.get_dish_compositions()
        
        # Собираем composition для текущего заказа
        order_compositions = [
            c for c in all_compositions 
            if c.dish_id in [item.dish_id for item in self.cart]
        ]
        
        order_quantities = {item.dish_id: item.quantity for item in self.cart}
        
        inventory = InventoryManager(products)
        shortages = inventory.check_availability(order_compositions, order_quantities)
        
        if shortages:
            shortage_text = "\n".join(shortages)
            messagebox.showwarning("Недостаточно продуктов", 
                f"На складе не хватает:\n\n{shortage_text}")
            return
        
        # Создаем заказ
        try:
            order_id = self.db.create_order(table_num, waiter.id)
            
            # Добавляем позиции и списываем продукты
            for item in self.cart:
                self.db.add_order_item(order_id, item.dish_id, item.quantity)
            
            # Списываем продукты
            updated = inventory.deduct_products(order_compositions, order_quantities)
            
            # Обновляем в БД
            for prod_id, new_qty in updated.items():
                self.db.update_product_quantity(prod_id, new_qty)
            
            # Занимаем столик
            self.db.occupy_table(table_num)
            
            # Показываем чек
            total = self.pricing.calculate_order_total(self.cart)
            receipt = f"ЧЕК №{order_id}\n{'═'*60}\n"
            receipt += f"Столик: {table_num} | Официант: {waiter.full_name}\n"
            receipt += f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            receipt += f"{'─'*60}\n"
            
            for item in self.cart:
                receipt += f"{item.name:35} {item.quantity:3} x {item.price:8.2f} = {item.subtotal:8.2f} ₽\n"
            
            receipt += f"{'─'*60}\n"
            receipt += f"{'ИТОГО:':>40} {total:15.2f} ₽"
            
            messagebox.showinfo("✅ Заказ оплачен", receipt)
            
            # Очищаем корзину
            self.cart = []
            self.refresh_cart_display()
            self.load_free_tables()
            self.load_menu()  # Обновляем остатки
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать заказ: {str(e)}")
    
    def free_table(self):
        """Освободить столик"""
        try:
            table_num = int(self.table_combo.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Выберите столик")
            return
        
        if messagebox.askyesno("Освободить", f"Освободить столик №{table_num}?"):
            self.db.free_table(table_num)
            self.load_free_tables()
            messagebox.showinfo("Готово", f"Столик №{table_num} свободен")


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = CafeApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()