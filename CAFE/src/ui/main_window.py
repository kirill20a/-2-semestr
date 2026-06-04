"""Главное окно официанта"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.database import get_connection
from src.ui.admin_panel import AdminPanel


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self.cart = []
        
        self.root.title("Кафе: Система обслуживания")
        self.root.geometry("750x650")
        self.root.configure(bg='#f0f0f0')
        
        self.build_widgets()
    
    def build_widgets(self):
        # Шапка
        header = tk.Frame(self.root, bg='#4a7c59', height=60)
        header.pack(fill='x')
        tk.Label(header, text="🍽️  КАФЕ «ВКУСНОЕ МЕСТО»", 
                 font=('Arial', 16, 'bold'), bg='#4a7c59', fg='white').pack(pady=12)
        
        # Выбор столика
        table_frame = tk.Frame(self.root, bg='#f0f0f0')
        table_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Label(table_frame, text="Столик №:", font=('Arial', 11), bg='#f0f0f0').pack(side='left')
        self.table_combo = ttk.Combobox(table_frame, state="readonly", width=5, font=('Arial', 12))
        self.table_combo.pack(side='left', padx=5)
        self.load_free_tables()
        
        tk.Label(table_frame, text="Официант:", font=('Arial', 11), bg='#f0f0f0').pack(side='left', padx=(20, 5))
        self.waiter_combo = ttk.Combobox(table_frame, state="readonly", width=30)
        self.waiter_combo.pack(side='left', padx=5)
        self.load_waiters()
        
        ttk.Button(table_frame, text="🆕 Новый заказ", command=self.new_order).pack(side='right', padx=10)
        
        # Выбор блюда
        dish_frame = tk.LabelFrame(self.root, text="📋 Меню", font=('Arial', 11, 'bold'), 
                                   bg='#f0f0f0', fg='#333')
        dish_frame.pack(fill='x', padx=15, pady=5)
        
        inner = tk.Frame(dish_frame, bg='#f0f0f0')
        inner.pack(padx=10, pady=10)
        
        tk.Label(inner, text="Блюдо:", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=0)
        self.dish_combo = ttk.Combobox(inner, state="readonly", width=40)
        self.dish_combo.grid(row=0, column=1, padx=5)
        
        tk.Label(inner, text="Кол-во:", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=2, padx=(10, 0))
        self.qty_entry = ttk.Entry(inner, width=6, font=('Arial', 11))
        self.qty_entry.grid(row=0, column=3, padx=5)
        self.qty_entry.insert(0, "1")
        
        ttk.Button(inner, text="➕ Добавить", command=self.add_to_cart).grid(row=0, column=4, padx=15)
        self.load_menu()
        
        # Корзина
        cart_frame = tk.LabelFrame(self.root, text="🧾 Текущий заказ", font=('Arial', 11, 'bold'), 
                                   bg='#f0f0f0', fg='#333')
        cart_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        self.cart_listbox = tk.Listbox(cart_frame, width=80, height=10, font=('Consolas', 10))
        self.cart_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(cart_frame, command=self.cart_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.cart_listbox.config(yscrollcommand=scrollbar.set)
        
        # Кнопки действий
        action_frame = tk.Frame(self.root, bg='#f0f0f0')
        action_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Button(action_frame, text="💰 Оплатить (Закрыть чек)", command=self.checkout).pack(side='left', padx=5)
        ttk.Button(action_frame, text="🆓 Освободить столик", command=self.free_table).pack(side='left', padx=5)
        ttk.Button(action_frame, text="❌ Отменить заказ", command=self.cancel_order).pack(side='left', padx=5)
        
        # Доп. окна
        windows_frame = tk.Frame(self.root, bg='#f0f0f0')
        windows_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        ttk.Button(windows_frame, text="🔧 Администрирование",command=lambda: AdminPanel(self.root, self.load_menu, self.load_free_tables, self.load_waiters)).pack(side='left', padx=5)
        ttk.Button(windows_frame, text="👨‍🍳 Экран кухни", command=self.open_kitchen).pack(side='left', padx=5)
        ttk.Button(windows_frame, text="📦 Склад продуктов", command=self.open_stock).pack(side='left', padx=5)
        ttk.Button(windows_frame, text="📊 Отчёты", command=self.open_reports).pack(side='left', padx=5)
        ttk.Button(windows_frame, text="📋 Все заказы", command=self.open_orders).pack(side='left', padx=5)
        ttk.Button(windows_frame, text="👥 Персонал и ЗП", command=self.open_staff).pack(side='left', padx=5)
    
    def load_free_tables(self):
        self.cursor.execute("SELECT table_number, is_occupied FROM tables_cafe ORDER BY table_number")
        all_tables = self.cursor.fetchall()
        free_list = []
        for num, occupied in all_tables:
            if occupied:
                free_list.append(f"{num} (занят)")
            else:
                free_list.append(str(num))
        self.table_combo['values'] = free_list
        for num, occupied in all_tables:
            if not occupied:
                self.table_combo.set(str(num))
                break
    
    def load_waiters(self):
        self.cursor.execute("""
            SELECT e.id, e.name || ' ' || e.surname 
            FROM employees e 
            JOIN job_titles j ON e.id_job_title = j.id 
            WHERE j.name = 'Официант'
        """)
        waiters = self.cursor.fetchall()
        self.waiters_dict = {name: wid for wid, name in waiters}
        self.waiter_combo['values'] = list(self.waiters_dict.keys())
        if self.waiters_dict:
            self.waiter_combo.set(list(self.waiters_dict.keys())[0])
    
    def load_menu(self):
        self.cursor.execute("SELECT id_dish, name_of_dish FROM menu WHERE is_available = 1")
        dishes = self.cursor.fetchall()
        self.dishes_dict = {name: did for did, name in dishes}
        self.dish_combo['values'] = list(self.dishes_dict.keys())
        if self.dishes_dict:
            self.dish_combo.set(list(self.dishes_dict.keys())[0])
    
    def new_order(self):
        if self.cart and not messagebox.askyesno("Новый заказ", "Текущий заказ будет потерян. Продолжить?"):
            return
        self.cart = []
        self.refresh_cart()
    
    def add_to_cart(self):
        dish_name = self.dish_combo.get()
        if not dish_name:
            messagebox.showwarning("Внимание", "Выберите блюдо из меню")
            return
        try:
            qty = int(self.qty_entry.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть целым положительным числом")
            return
        dish_id = self.dishes_dict[dish_name]
        for item in self.cart:
            if item[0] == dish_id:
                item[1] += qty
                self.refresh_cart()
                return
        self.cart.append([dish_id, qty, dish_name])
        self.refresh_cart()
    
    def refresh_cart(self):
        self.cart_listbox.delete(0, tk.END)
        total = 0
        for dish_id, qty, name in self.cart:
            self.cursor.execute("SELECT price FROM menu WHERE id_dish = ?", (dish_id,))
            price = self.cursor.fetchone()[0]
            subtotal = price * qty
            total += subtotal
            self.cart_listbox.insert(tk.END, f"{name:35} {qty:3} x {price:8.2f} = {subtotal:8.2f} ₽")
        self.cart_listbox.insert(tk.END, "─" * 65)
        self.cart_listbox.insert(tk.END, f"{'ИТОГО:':>40} {total:15.2f} ₽")
    
    def cancel_order(self):
        self.cart = []
        self.refresh_cart()
        messagebox.showinfo("Отмена", "Заказ отменён")
    
    def free_table(self):
        table_str = self.table_combo.get().replace(" (занят)", "")
        table_num = int(table_str)
        self.cursor.execute("SELECT is_occupied FROM tables_cafe WHERE table_number = ?", (table_num,))
        result = self.cursor.fetchone()
        if result and result[0] == 0:
            messagebox.showinfo("Инфо", f"Столик №{table_num} уже свободен")
            return
        if messagebox.askyesno("Освободить", f"Освободить столик №{table_num}?"):
            self.cursor.execute("UPDATE tables_cafe SET is_occupied = 0 WHERE table_number = ?", (table_num,))
            self.conn.commit()
            self.load_free_tables()
            messagebox.showinfo("Готово", f"Столик №{table_num} свободен")
    
    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Корзина пуста", "Добавьте блюда в заказ")
            return
        table_str = self.table_combo.get().replace(" (занят)", "")
        if not table_str.isdigit():
            messagebox.showwarning("Ошибка", "Выберите свободный столик")
            return
        table_num = int(table_str)
        self.cursor.execute("SELECT is_occupied FROM tables_cafe WHERE table_number = ?", (table_num,))
        result = self.cursor.fetchone()
        if result and result[0] == 1:
            messagebox.showwarning("Столик занят", f"Столик №{table_num} уже занят!")
            return
        shortages = self.check_products()
        if shortages:
            self.handle_shortages(shortages)
        else:
            self.complete_order()
    
    def check_products(self):
        needed = {}
        for dish_id, qty, _ in self.cart:
            self.cursor.execute("SELECT id_product, quantity FROM dish_composition WHERE id_dish = ?", (dish_id,))
            for prod_id, qty_per_portion in self.cursor.fetchall():
                needed[prod_id] = needed.get(prod_id, 0) + (qty_per_portion * qty)
        shortages = []
        for prod_id, total_needed in needed.items():
            self.cursor.execute("SELECT name_of_product, quantity_at_storage FROM products WHERE id_product = ?", (prod_id,))
            name, stock = self.cursor.fetchone()
            if stock < total_needed:
                shortages.append((prod_id, name, stock, total_needed))
        return shortages
    
    def handle_shortages(self, shortages):
        dialog = tk.Toplevel(self.root)
        dialog.title("⚠️ Недостаточно продуктов")
        dialog.geometry("450x300")
        dialog.configure(bg='#fff8e1')
        tk.Label(dialog, text="На складе не хватает:", font=('Arial', 11, 'bold'), bg='#fff8e1', fg='#c62828').pack(pady=10)
        for _, name, stock, needed in shortages:
            tk.Label(dialog, text=f"• {name}: есть {stock:.3f}, нужно {needed:.3f}", bg='#fff8e1', font=('Arial', 10)).pack()
        tk.Label(dialog, text="\nЗаказать недостающие продукты у поставщика?", bg='#fff8e1', font=('Arial', 10)).pack(pady=10)
        
        def restock_all():
            for pid, _, _, needed in shortages:
                self.cursor.execute("UPDATE products SET quantity_at_storage = quantity_at_storage + ? WHERE id_product = ?",
                                    (needed * 1.5, pid))
            self.conn.commit()
            messagebox.showinfo("Успех", "Продукты заказаны!")
            dialog.destroy()
            self.complete_order()
        
        btn_frame = tk.Frame(dialog, bg='#fff8e1')
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="✅ Заказать и продолжить", command=restock_all).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="❌ Отменить", command=dialog.destroy).pack(side='left', padx=10)
    
    def complete_order(self):
        table_num = int(self.table_combo.get().replace(" (занят)", ""))
        waiter_name = self.waiter_combo.get()
        waiter_id = self.waiters_dict.get(waiter_name, 1)
        order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO orders (table_num, id_employee, created_at, status) VALUES (?, ?, ?, 'Готовится')",
                            (table_num, waiter_id, order_date))
        order_id = self.cursor.lastrowid
        self.cursor.execute("UPDATE tables_cafe SET is_occupied = 1 WHERE table_number = ?", (table_num,))
        
        total = 0
        for dish_id, qty, name in self.cart:
            self.cursor.execute("SELECT price FROM menu WHERE id_dish = ?", (dish_id,))
            price = self.cursor.fetchone()[0]
            total += price * qty
            self.cursor.execute("INSERT INTO order_items (id_order, id_dish, quantity, ready_status) VALUES (?, ?, ?, 0)",
                                (order_id, dish_id, qty))
            self.cursor.execute("SELECT id_product, quantity FROM dish_composition WHERE id_dish = ?", (dish_id,))
            for prod_id, qty_per_portion in self.cursor.fetchall():
                self.cursor.execute("UPDATE products SET quantity_at_storage = quantity_at_storage - ? WHERE id_product = ?",
                                    (qty_per_portion * qty, prod_id))
        
        self.conn.commit()
        messagebox.showinfo("✅ Заказ оплачен", f"Чек №{order_id}\nСтолик: {table_num}\nСумма: {total:.2f} ₽")
        self.cart = []
        self.refresh_cart()
        self.load_menu()
        self.load_free_tables()
    
    def open_kitchen(self):
        from src.ui.kitchen_window import KitchenWindow
        KitchenWindow(self.root)
    
    def open_stock(self):
        from src.ui.stock_window import StockWindow
        StockWindow(self.root)
    
    def open_reports(self):
        from src.ui.reports_window import ReportsWindow
        ReportsWindow(self.root)
    
    def open_orders(self):
        from src.ui.orders_window import OrdersWindow
        OrdersWindow(self.root)
    
    def open_staff(self):
        from src.ui.staff_window import StaffWindow
        StaffWindow(self.root)
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()