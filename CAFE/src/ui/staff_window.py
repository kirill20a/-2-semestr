"""Окно персонала и зарплаты"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from src.database import get_connection


class StaffWindow:
    def __init__(self, parent):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        
        self.window = tk.Toplevel(parent)
        self.window.title("👥 Персонал и зарплата")
        self.window.geometry("850x550")
        self.window.configure(bg='#fafafa')
        
        tk.Label(self.window, text="Персонал и расчёт зарплаты", font=('Arial', 14, 'bold'), bg='#fafafa').pack(pady=10)
        
        f1 = tk.Frame(self.window, bg='#fafafa')
        f1.pack(pady=5)
        tk.Label(f1, text="Месяц (ГГГГ-ММ):", bg='#fafafa').pack(side='left')
        self.month_entry = ttk.Entry(f1, width=10, font=('Arial', 10))
        self.month_entry.pack(side='left', padx=10)
        self.month_entry.insert(0, datetime.now().strftime('%Y-%m'))
        
        tree_frame = tk.Frame(self.window, bg='#fafafa')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(tree_frame, 
                                  columns=('ФИО', 'Должность', 'Оклад', '%', 'База', 'Премия', 'Итого'),
                                  show='headings', height=12, yscrollcommand=scrollbar.set)
        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('ФИО', text='ФИО')
        self.tree.heading('Должность', text='Должность')
        self.tree.heading('Оклад', text='Оклад')
        self.tree.heading('%', text='%')
        self.tree.heading('База', text='База для премии')
        self.tree.heading('Премия', text='Премия')
        self.tree.heading('Итого', text='Итого')
        
        self.tree.column('ФИО', width=200)
        self.tree.column('Должность', width=130)
        self.tree.column('Оклад', width=100, anchor='center')
        self.tree.column('%', width=50, anchor='center')
        self.tree.column('База', width=150, anchor='center')
        self.tree.column('Премия', width=120, anchor='center')
        self.tree.column('Итого', width=120, anchor='center')
        
        self.total_label = tk.Label(self.window, text="", font=('Arial', 11, 'bold'), bg='#fafafa', fg='#4a7c59')
        self.total_label.pack(pady=5)
        
        ttk.Button(self.window, text="🔄 Рассчитать", command=self.refresh).pack(pady=5)
        self.refresh()
    
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        month_val = self.month_entry.get()
        
        # Общая выручка
        self.cursor.execute('''
            SELECT COALESCE(SUM(m.price * oi.quantity), 0)
            FROM orders o
            JOIN order_items oi ON o.id_order = oi.id_order
            JOIN menu m ON oi.id_dish = m.id_dish
            WHERE strftime('%Y-%m', o.created_at) = ? AND o.status IN ('Оплачен', 'Выполнен')
        ''', (month_val,))
        total_revenue = self.cursor.fetchone()[0]
        
        # Выручка бара
        self.cursor.execute('''
            SELECT COALESCE(SUM(m.price * oi.quantity), 0)
            FROM orders o
            JOIN order_items oi ON o.id_order = oi.id_order
            JOIN menu m ON oi.id_dish = m.id_dish
            JOIN categories c ON m.id_category = c.id_category
            WHERE strftime('%Y-%m', o.created_at) = ? AND o.status IN ('Оплачен', 'Выполнен') AND c.name_category = 'Напитки'
        ''', (month_val,))
        bar_revenue = self.cursor.fetchone()[0]
        kitchen_revenue = total_revenue - bar_revenue
        
        total_payroll = 0
        
        self.cursor.execute('''
            SELECT e.id, e.name || ' ' || e.surname, j.name, j.salary_base, j.bonus_percent
            FROM employees e
            JOIN job_titles j ON e.id_job_title = j.id
            ORDER BY j.name, e.name
        ''')
        
        for emp_id, emp_name, pos, salary, bonus_pct in self.cursor.fetchall():
            salary = salary or 0
            bonus_pct = bonus_pct or 0
            
            if pos == 'Официант':
                self.cursor.execute('''
                    SELECT COALESCE(SUM(m.price * oi.quantity), 0)
                    FROM orders o
                    JOIN order_items oi ON o.id_order = oi.id_order
                    JOIN menu m ON oi.id_dish = m.id_dish
                    WHERE o.id_employee = ? AND strftime('%Y-%m', o.created_at) = ? AND o.status IN ('Оплачен', 'Выполнен')
                ''', (emp_id, month_val))
                base = self.cursor.fetchone()[0]
                base_text = f"Личная: {base:.2f} ₽"
            elif 'Бариста' in pos or 'Бармен' in pos:
                self.cursor.execute("SELECT COUNT(*) FROM employees e JOIN job_titles j ON e.id_job_title = j.id WHERE j.name LIKE '%Бариста%' OR j.name LIKE '%Бармен%'")
                cnt = self.cursor.fetchone()[0] or 1
                base = bar_revenue / cnt
                base_text = f"Бар: {bar_revenue:.2f} ÷ {cnt}"
            elif 'Повар' in pos or 'Шеф' in pos:
                self.cursor.execute("SELECT COUNT(*) FROM employees e JOIN job_titles j ON e.id_job_title = j.id WHERE j.name LIKE '%Повар%' OR j.name LIKE '%Шеф%'")
                cnt = self.cursor.fetchone()[0] or 1
                base = kitchen_revenue / cnt
                base_text = f"Кухня: {kitchen_revenue:.2f} ÷ {cnt}"
            else:
                self.cursor.execute("SELECT COUNT(*) FROM employees e JOIN job_titles j ON e.id_job_title = j.id WHERE j.name IN ('Администратор', 'Администратор зала', 'Управляющий')")
                cnt = self.cursor.fetchone()[0] or 1
                base = total_revenue / cnt
                base_text = f"Общая: {total_revenue:.2f} ÷ {cnt}"
            
            bonus = base * bonus_pct / 100
            total = salary + bonus
            total_payroll += total
            
            self.tree.insert('', 'end', values=(emp_name, pos, f"{salary:.2f}", f"{bonus_pct}%", base_text, f"{bonus:.2f}", f"{total:.2f}"))
        
        self.total_label.config(text=f"Фонд оплаты труда за {month_val}: {total_payroll:.2f} ₽ | Выручка: {total_revenue:.2f} ₽")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()