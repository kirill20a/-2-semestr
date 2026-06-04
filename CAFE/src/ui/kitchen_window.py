"""Окно кухни"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.database import get_connection


class KitchenWindow:
    def __init__(self, parent):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        
        self.window = tk.Toplevel(parent)
        self.window.title("👨‍🍳 Экран кухни")
        self.window.geometry("850x450")
        self.window.configure(bg='#fafafa')
        
        tk.Label(self.window, text="Блюда, ожидающие приготовления", 
                 font=('Arial', 13, 'bold'), bg='#fafafa').pack(pady=10)
        
        tree_frame = tk.Frame(self.window, bg='#fafafa')
        tree_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(tree_frame, columns=('Чек', 'Стол', 'Блюдо', 'Кол-во', 'Время'), 
                                  show='headings', height=12, yscrollcommand=scrollbar.set)
        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('Чек', text='№ Заказа')
        self.tree.heading('Стол', text='Стол')
        self.tree.heading('Блюдо', text='Блюдо')
        self.tree.heading('Кол-во', text='Кол-во')
        self.tree.heading('Время', text='Время (мин)')
        
        self.tree.column('Чек', width=80, anchor='center')
        self.tree.column('Стол', width=60, anchor='center')
        self.tree.column('Блюдо', width=280)
        self.tree.column('Кол-во', width=70, anchor='center')
        self.tree.column('Время', width=120, anchor='center')
        
        btn_frame = tk.Frame(self.window, bg='#fafafa')
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.refresh).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✅ Отметить готовым", command=self.mark_ready).pack(side='left', padx=5)
        
        self.refresh()
    
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute('''
            SELECT o.id_order, o.table_num, m.name_of_dish, oi.quantity, m.cooking_time
            FROM order_items oi
            JOIN orders o ON oi.id_order = o.id_order
            JOIN menu m ON oi.id_dish = m.id_dish
            WHERE oi.ready_status = 0 AND o.status IN ('Готовится', 'Оплачен', 'Выполнен')
            ORDER BY o.created_at ASC
        ''')
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=row)
    
    def mark_ready(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Не выбрано", "Выберите блюдо")
            return
        item = self.tree.item(selected[0])
        order_id = item['values'][0]
        dish_name = item['values'][2]
        self.cursor.execute('''
            UPDATE order_items SET ready_status = 1 
            WHERE id_order = ? AND id_dish = (SELECT id_dish FROM menu WHERE name_of_dish = ?)
        ''', (order_id, dish_name))
        self.cursor.execute("SELECT COUNT(*) FROM order_items WHERE id_order = ? AND ready_status = 0", (order_id,))
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("UPDATE orders SET status = 'Выполнен' WHERE id_order = ?", (order_id,))
            self.cursor.execute("UPDATE tables_cafe SET is_occupied = 0 WHERE table_number = (SELECT table_num FROM orders WHERE id_order = ?)", (order_id,))
        self.conn.commit()
        self.refresh()
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()