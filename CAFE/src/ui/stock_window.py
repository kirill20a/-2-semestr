"""Окно склада"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.database import get_connection


class StockWindow:
    def __init__(self, parent):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        
        self.window = tk.Toplevel(parent)
        self.window.title("📦 Склад продуктов")
        self.window.geometry("900x550")
        
        filter_frame = tk.Frame(self.window, bg='#f5f5f5')
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(filter_frame, text="Поиск:", bg='#f5f5f5').pack(side='left', padx=5)
        self.search_entry = ttk.Entry(filter_frame, width=30)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<Return>', lambda e: self.refresh())
        
        tree_frame = tk.Frame(self.window)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(tree_frame, 
                                  columns=('ID', 'Название', 'Ед.', 'Остаток', 'Себест.', 'Статус'),
                                  show='headings', height=20, yscrollcommand=scrollbar.set)
        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Название', text='Название продукта')
        self.tree.heading('Ед.', text='Ед.')
        self.tree.heading('Остаток', text='Остаток')
        self.tree.heading('Себест.', text='Себест. (руб)')
        self.tree.heading('Статус', text='Статус')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Название', width=250)
        self.tree.column('Ед.', width=60, anchor='center')
        self.tree.column('Остаток', width=80, anchor='center')
        self.tree.column('Себест.', width=100, anchor='center')
        self.tree.column('Статус', width=140, anchor='center')
        
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.refresh).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📦 Пополнить выбранное", command=self.manual_restock).pack(side='left', padx=5)
        
        self.stats_label = tk.Label(self.window, text="", font=('Arial', 10, 'bold'), bg='#f5f5f5')
        self.stats_label.pack(pady=5)
        
        self.refresh()
    
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        search = self.search_entry.get()
        query = "SELECT id_product, name_of_product, unit, quantity_at_storage, cost_per_unit FROM products WHERE 1=1"
        params = []
        if search:
            query += " AND name_of_product LIKE ?"
            params.append(f'%{search}%')
        query += " ORDER BY quantity_at_storage ASC"
        self.cursor.execute(query, params)
        
        total_value = 0
        low_stock_count = 0
        for pid, name, unit, qty, cost in self.cursor.fetchall():
            total_value += cost * qty
            if qty == 0:
                status, tags = "🔴 Нет", ('out',)
            elif qty < 1.0:
                status, tags = "🟡 Мало", ('low',)
                low_stock_count += 1
            else:
                status, tags = "🟢 Норма", ('ok',)
            self.tree.insert('', 'end', values=(pid, name, unit, f"{qty:.3f}", f"{cost:.2f}", status), tags=tags)
        
        self.tree.tag_configure('out', background='#ffcccc')
        self.tree.tag_configure('low', background='#ffffcc')
        self.tree.tag_configure('ok', background='#ccffcc')
        
        self.stats_label.config(text=f"Всего: {len(self.tree.get_children())} | Заканчивается: {low_stock_count} | Себестоимость: {total_value:.2f} ₽")
    
    def manual_restock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Не выбрано", "Выберите продукт")
            return
        item = self.tree.item(selected[0])
        pid, name, _, qty_str = item['values'][0], item['values'][1], None, item['values'][3]
        
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Пополнение: {name}")
        dialog.geometry("300x150")
        tk.Label(dialog, text=f"Текущий остаток: {qty_str}").pack(pady=10)
        tk.Label(dialog, text="Добавить:").pack()
        entry = ttk.Entry(dialog, width=20)
        entry.pack(pady=5)
        entry.focus()
        
        def do_restock():
            try:
                qty = float(entry.get())
                if qty <= 0:
                    raise ValueError
                self.cursor.execute("UPDATE products SET quantity_at_storage = quantity_at_storage + ? WHERE id_product = ?", (qty, pid))
                self.conn.commit()
                messagebox.showinfo("Успех", f"Добавлено {qty} ед.")
                dialog.destroy()
                self.refresh()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите положительное число")
        
        ttk.Button(dialog, text="✅ Пополнить", command=do_restock).pack(pady=10)
        entry.bind('<Return>', lambda e: do_restock())
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()