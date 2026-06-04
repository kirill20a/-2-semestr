"""Окно отчётов"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from src.database import get_connection


class ReportsWindow:
    def __init__(self, parent):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Отчёты")
        self.window.geometry("700x500")
        self.window.configure(bg='#fafafa')
        
        tk.Label(self.window, text="Отчёты кафе", font=('Arial', 14, 'bold'), bg='#fafafa').pack(pady=10)
        
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Вкладка Выручка
        tab1 = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab1, text="💰 Выручка")
        self.build_revenue_tab(tab1)
        
        # Вкладка ТОП-5
        tab2 = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab2, text="🏆 ТОП-5")
        self.build_top5_tab(tab2)
    
    def build_revenue_tab(self, parent):
        tk.Label(parent, text="Дата:", bg='#fafafa').pack(pady=5)
        self.date_entry = ttk.Entry(parent, width=15, font=('Arial', 11))
        self.date_entry.pack()
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        self.rev_text = tk.Text(parent, width=70, height=20, font=('Consolas', 10))
        self.rev_text.pack(padx=10, pady=10)
        ttk.Button(parent, text="📈 Показать", command=self.show_revenue).pack()
    
    def show_revenue(self):
        date_val = self.date_entry.get()
        self.rev_text.delete(1.0, tk.END)
        
        self.cursor.execute('''
            SELECT COALESCE(SUM(m.price * oi.quantity), 0), COUNT(DISTINCT o.id_order)
            FROM orders o
            JOIN order_items oi ON o.id_order = oi.id_order
            JOIN menu m ON oi.id_dish = m.id_dish
            WHERE DATE(o.created_at) = ? AND o.status IN ('Оплачен', 'Выполнен')
        ''', (date_val,))
        rev, checks = self.cursor.fetchone()
        
        self.rev_text.insert(tk.END, f"=== ОТЧЁТ ЗА {date_val} ===\n\n")
        self.rev_text.insert(tk.END, f"Чеков: {checks}\nВыручка: {rev:.2f} ₽\n\n")
        
        self.cursor.execute('''
            SELECT e.name || ' ' || e.surname, COUNT(DISTINCT o.id_order), COALESCE(SUM(m.price * oi.quantity), 0)
            FROM orders o
            JOIN employees e ON o.id_employee = e.id
            JOIN order_items oi ON o.id_order = oi.id_order
            JOIN menu m ON oi.id_dish = m.id_dish
            WHERE DATE(o.created_at) = ? AND o.status IN ('Оплачен', 'Выполнен')
            GROUP BY e.id ORDER BY SUM(m.price * oi.quantity) DESC
        ''', (date_val,))
        self.rev_text.insert(tk.END, "ПО ОФИЦИАНТАМ:\n")
        for name, cnt, s in self.cursor.fetchall():
            self.rev_text.insert(tk.END, f"  {name}: {cnt} чеков, {s:.2f} ₽\n")
    
    def build_top5_tab(self, parent):
        self.top5_text = tk.Text(parent, width=70, height=20, font=('Consolas', 10))
        self.top5_text.pack(padx=10, pady=10)
        ttk.Button(parent, text="🔄 Обновить", command=self.show_top5).pack()
        self.show_top5()
    
    def show_top5(self):
        self.top5_text.delete(1.0, tk.END)
        self.cursor.execute('''
            SELECT m.name_of_dish, SUM(oi.quantity)
            FROM order_items oi
            JOIN menu m ON oi.id_dish = m.id_dish
            JOIN orders o ON oi.id_order = o.id_order
            WHERE o.status IN ('Оплачен', 'Выполнен')
            GROUP BY m.id_dish ORDER BY SUM(oi.quantity) DESC LIMIT 5
        ''')
        self.top5_text.insert(tk.END, "=== ТОП-5 БЛЮД ===\n\n")
        for i, (name, qty) in enumerate(self.cursor.fetchall(), 1):
            self.top5_text.insert(tk.END, f"{i}. {name}: {qty} порций\n")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()