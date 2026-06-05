"""Окно всех заказов"""
import tkinter as tk
from tkinter import ttk
from src.database import get_connection


class OrdersWindow:
    def __init__(self, parent):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        
        self.window = tk.Toplevel(parent)
        self.window.title("📋 Все заказы")
        self.window.geometry("900x400")
        
        self.tree = ttk.Treeview(self.window, columns=('ID', 'Стол', 'Официант', 'Дата', 'Статус'), 
                                  show='headings', height=15)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tree.heading('ID', text='№')
        self.tree.heading('Стол', text='Стол')
        self.tree.heading('Официант', text='Официант')
        self.tree.heading('Дата', text='Дата и время')
        self.tree.heading('Статус', text='Статус')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Стол', width=50, anchor='center')
        self.tree.column('Официант', width=200)
        self.tree.column('Дата', width=180, anchor='center')
        self.tree.column('Статус', width=100, anchor='center')
        
        ttk.Button(self.window, text="🔄 Обновить", command=self.refresh).pack(pady=5)
        self.refresh()
    
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute('''
            SELECT o.id_order, o.table_num, e.name || ' ' || e.surname, o.created_at, o.status 
            FROM orders o
            JOIN employees e ON o.id_employee = e.id
            ORDER BY o.id_order DESC LIMIT 50
        ''')
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=row)
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()