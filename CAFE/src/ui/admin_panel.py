"""Панель администратора — все настройки в одном окне"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.database import get_connection


class AdminPanel:
    def __init__(self, parent, load_menu_callback=None, load_tables_callback=None, load_waiters_callback=None):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self.load_menu = load_menu_callback
        self.load_tables = load_tables_callback
        self.load_waiters = load_waiters_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("🔧 Панель администратора")
        self.window.geometry("800x600")
        self.window.configure(bg='#fafafa')
        
        tk.Label(self.window, text="Панель администратора", font=('Arial', 14, 'bold'), bg='#fafafa').pack(pady=10)
        
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Вкладки
        self.build_menu_tab(notebook)
        self.build_composition_tab(notebook)
        self.build_products_tab(notebook)
        self.build_employees_tab(notebook)
        self.build_categories_tab(notebook)
        self.build_positions_tab(notebook)
        self.build_tables_tab(notebook)
    
    # ============================================================
    # ВКЛАДКА: МЕНЮ
    # ============================================================
    def build_menu_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab, text="📋 Меню")
        
        tree_frame = tk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        sb = ttk.Scrollbar(tree_frame)
        sb.pack(side='right', fill='y')
        
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Название', 'Цена', 'Категория', 'Время', 'Доступно'),
                            show='headings', height=10, yscrollcommand=sb.set)
        tree.pack(fill='both', expand=True)
        sb.config(command=tree.yview)
        
        for col, w in [('ID', 40), ('Название', 180), ('Цена', 80), ('Категория', 120), ('Время', 80), ('Доступно', 80)]:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center' if col != 'Название' else 'w')
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            self.cursor.execute('''
                SELECT m.id_dish, m.name_of_dish, m.price, c.name_category, m.cooking_time, m.is_available
                FROM menu m JOIN categories c ON m.id_category = c.id_category ORDER BY m.id_dish
            ''')
            for row in self.cursor.fetchall():
                did, name, price, cat, time, avail = row
                tree.insert('', 'end', values=(did, name, f"{price:.2f}", cat, time, '✅' if avail else '❌'))
        
        form = tk.Frame(tab)
        form.pack(fill='x', padx=10, pady=5)
        name_e = ttk.Entry(form, width=20)
        name_e.pack(side='left', padx=2)
        price_e = ttk.Entry(form, width=8)
        price_e.pack(side='left', padx=2)
        time_e = ttk.Entry(form, width=6)
        time_e.pack(side='left', padx=2)
        
        def add():
            try:
                self.cursor.execute("INSERT INTO menu (name_of_dish, price, id_category, cooking_time) VALUES (?, ?, 1, ?)",
                                   (name_e.get(), float(price_e.get()), int(time_e.get() or 10)))
                self.conn.commit()
                refresh()
                if self.load_menu: self.load_menu()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверные числа")
        
        def edit():
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel[0])
            did = item['values'][0]
            try:
                self.cursor.execute("UPDATE menu SET name_of_dish=?, price=?, cooking_time=? WHERE id_dish=?",
                                   (name_e.get() or item['values'][1],
                                    float(price_e.get() or item['values'][2]),
                                    int(time_e.get() or item['values'][4]), did))
                self.conn.commit()
                refresh()
                if self.load_menu: self.load_menu()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверные числа")
        
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno("Удалить", "Удалить блюдо?"):
                did = tree.item(sel[0])['values'][0]
                self.cursor.execute("DELETE FROM menu WHERE id_dish=?", (did,))
                self.conn.commit()
                refresh()
                if self.load_menu: self.load_menu()
        
        def toggle():
            sel = tree.selection()
            if sel:
                did = tree.item(sel[0])['values'][0]
                self.cursor.execute("UPDATE menu SET is_available = 1 - is_available WHERE id_dish=?", (did,))
                self.conn.commit()
                refresh()
                if self.load_menu: self.load_menu()
        
        btn = tk.Frame(tab)
        btn.pack(pady=5)
        ttk.Button(btn, text="➕", command=add).pack(side='left', padx=2)
        ttk.Button(btn, text="✏️", command=edit).pack(side='left', padx=2)
        ttk.Button(btn, text="🗑️", command=delete).pack(side='left', padx=2)
        ttk.Button(btn, text="🔄 Вкл/Выкл", command=toggle).pack(side='left', padx=2)
        refresh()
    
    # ============================================================
    # ВКЛАДКА: СОСТАВ БЛЮД
    # ============================================================
    def build_composition_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab, text="🧪 Состав")
        
        top = tk.Frame(tab)
        top.pack(fill='x', padx=10, pady=5)
        tk.Label(top, text="Блюдо:").pack(side='left')
        dish_cb = ttk.Combobox(top, state='readonly', width=30)
        dish_cb.pack(side='left', padx=5)
        self.cursor.execute("SELECT id_dish, name_of_dish FROM menu ORDER BY name_of_dish")
        dishes = {name: did for did, name in self.cursor.fetchall()}
        dish_cb['values'] = list(dishes.keys())
        if dishes: dish_cb.set(list(dishes.keys())[0])
        
        tree_frame = tk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        sb = ttk.Scrollbar(tree_frame)
        sb.pack(side='right', fill='y')
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Продукт', 'Кол-во'), show='headings', height=8, yscrollcommand=sb.set)
        tree.pack(fill='both', expand=True)
        sb.config(command=tree.yview)
        tree.heading('ID', text='ID')
        tree.heading('Продукт', text='Продукт')
        tree.heading('Кол-во', text='Кол-во на порцию')
        tree.column('ID', width=50, anchor='center')
        tree.column('Продукт', width=250)
        tree.column('Кол-во', width=150, anchor='center')
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            name = dish_cb.get()
            if name not in dishes: return
            self.cursor.execute('''
                SELECT dc.id, p.name_of_product, dc.quantity
                FROM dish_composition dc
                JOIN products p ON dc.id_product = p.id_product
                WHERE dc.id_dish = ?
            ''', (dishes[name],))
            for row in self.cursor.fetchall():
                tree.insert('', 'end', values=row)
        
        ttk.Button(top, text="📋 Показать", command=refresh).pack(side='left', padx=5)
        
        add_f = tk.Frame(tab)
        add_f.pack(fill='x', padx=10, pady=5)
        tk.Label(add_f, text="Продукт:").pack(side='left')
        prod_cb = ttk.Combobox(add_f, width=25)
        prod_cb.pack(side='left', padx=5)
        self.cursor.execute("SELECT id_product, name_of_product FROM products ORDER BY name_of_product")
        prods = {name: pid for pid, name in self.cursor.fetchall()}
        prod_cb['values'] = list(prods.keys())
        tk.Label(add_f, text="Кол-во:").pack(side='left')
        qty_e = ttk.Entry(add_f, width=8)
        qty_e.pack(side='left', padx=5)
        
        def add_ingredient():
            if dish_cb.get() in dishes and prod_cb.get() in prods:
                try:
                    self.cursor.execute("INSERT INTO dish_composition (id_dish, id_product, quantity) VALUES (?, ?, ?)",
                                       (dishes[dish_cb.get()], prods[prod_cb.get()], float(qty_e.get())))
                    self.conn.commit()
                    refresh()
                except ValueError:
                    pass
        
        ttk.Button(add_f, text="➕", command=add_ingredient).pack(side='left', padx=5)
        refresh()
    
    # ============================================================
    # ВКЛАДКА: ПРОДУКТЫ
    # ============================================================
    def build_products_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab, text="📦 Продукты")
        
        tree_frame = tk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        sb = ttk.Scrollbar(tree_frame)
        sb.pack(side='right', fill='y')
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Название', 'Ед.', 'Остаток', 'Себест.'),
                            show='headings', height=12, yscrollcommand=sb.set)
        tree.pack(fill='both', expand=True)
        sb.config(command=tree.yview)
        for col, w in [('ID', 40), ('Название', 200), ('Ед.', 60), ('Остаток', 80), ('Себест.', 80)]:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center' if col != 'Название' else 'w')
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            self.cursor.execute("SELECT id_product, name_of_product, unit, quantity_at_storage, cost_per_unit FROM products ORDER BY id_product")
            for row in self.cursor.fetchall():
                tree.insert('', 'end', values=row)
        
        form = tk.Frame(tab)
        form.pack(fill='x', padx=10, pady=5)
        name_e = ttk.Entry(form, width=20)
        name_e.pack(side='left', padx=2)
        unit_e = ttk.Entry(form, width=6)
        unit_e.pack(side='left', padx=2)
        cost_e = ttk.Entry(form, width=8)
        cost_e.pack(side='left', padx=2)
        
        def add():
            try:
                self.cursor.execute("INSERT INTO products (name_of_product, unit, cost_per_unit) VALUES (?, ?, ?)",
                                   (name_e.get(), unit_e.get(), float(cost_e.get())))
                self.conn.commit()
                refresh()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверная цена")
        
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno("Удалить", "Удалить продукт?"):
                self.cursor.execute("DELETE FROM products WHERE id_product=?", (tree.item(sel[0])['values'][0],))
                self.conn.commit()
                refresh()
        
        ttk.Button(form, text="➕", command=add).pack(side='left', padx=2)
        ttk.Button(tab, text="🗑️ Удалить", command=delete).pack(pady=5)
        refresh()
    
    # ============================================================
    # ВКЛАДКА: СОТРУДНИКИ
    # ============================================================
    def build_employees_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab, text="👤 Сотрудники")
        
        tree_frame = tk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        sb = ttk.Scrollbar(tree_frame)
        sb.pack(side='right', fill='y')
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Имя', 'Фамилия', 'Должность'),
                            show='headings', height=12, yscrollcommand=sb.set)
        tree.pack(fill='both', expand=True)
        sb.config(command=tree.yview)
        for col, w in [('ID', 40), ('Имя', 150), ('Фамилия', 150), ('Должность', 150)]:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center' if col == 'ID' else 'w')
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            self.cursor.execute('''
                SELECT e.id, e.name, e.surname, j.name
                FROM employees e JOIN job_titles j ON e.id_job_title = j.id ORDER BY e.id
            ''')
            for row in self.cursor.fetchall():
                tree.insert('', 'end', values=row)
        
        form = tk.Frame(tab)
        form.pack(fill='x', padx=10, pady=5)
        name_e = ttk.Entry(form, width=15)
        name_e.pack(side='left', padx=2)
        surname_e = ttk.Entry(form, width=15)
        surname_e.pack(side='left', padx=2)
        pos_cb = ttk.Combobox(form, width=15, state='readonly')
        pos_cb.pack(side='left', padx=2)
        self.cursor.execute("SELECT name FROM job_titles")
        pos_cb['values'] = [r[0] for r in self.cursor.fetchall()]
        
        def add():
            if name_e.get() and surname_e.get() and pos_cb.get():
                self.cursor.execute("SELECT id FROM job_titles WHERE name=?", (pos_cb.get(),))
                pid = self.cursor.fetchone()[0]
                self.cursor.execute("INSERT INTO employees (name, surname, id_job_title) VALUES (?, ?, ?)",
                                   (name_e.get(), surname_e.get(), pid))
                self.conn.commit()
                refresh()
                if self.load_waiters: self.load_waiters()
        
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno("Удалить", "Удалить сотрудника?"):
                self.cursor.execute("DELETE FROM employees WHERE id=?", (tree.item(sel[0])['values'][0],))
                self.conn.commit()
                refresh()
                if self.load_waiters: self.load_waiters()
        
        ttk.Button(form, text="➕", command=add).pack(side='left', padx=2)
        ttk.Button(tab, text="🗑️ Удалить", command=delete).pack(pady=5)
        refresh()
    
    # ============================================================
    # ВКЛАДКА: КАТЕГОРИИ
    # ============================================================
    def build_categories_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab, text="📁 Категории")
        
        tree = ttk.Treeview(tab, columns=('ID', 'Название'), show='headings', height=12)
        tree.pack(fill='both', expand=True, padx=10, pady=5)
        tree.heading('ID', text='ID')
        tree.heading('Название', text='Название')
        tree.column('ID', width=50, anchor='center')
        tree.column('Название', width=300)
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            self.cursor.execute("SELECT id_category, name_category FROM categories ORDER BY id_category")
            for row in self.cursor.fetchall():
                tree.insert('', 'end', values=row)
        
        form = tk.Frame(tab)
        form.pack(fill='x', padx=10, pady=5)
        name_e = ttk.Entry(form, width=30)
        name_e.pack(side='left', padx=2)
        
        def add():
            if name_e.get():
                self.cursor.execute("INSERT OR IGNORE INTO categories (name_category) VALUES (?)", (name_e.get(),))
                self.conn.commit()
                refresh()
        
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno("Удалить", "Удалить категорию?"):
                self.cursor.execute("DELETE FROM categories WHERE id_category=?", (tree.item(sel[0])['values'][0],))
                self.conn.commit()
                refresh()
        
        ttk.Button(form, text="➕", command=add).pack(side='left', padx=2)
        ttk.Button(tab, text="🗑️ Удалить", command=delete).pack(pady=5)
        refresh()
    
    # ============================================================
    # ВКЛАДКА: ДОЛЖНОСТИ
    # ============================================================
    def build_positions_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab, text="💼 Должности")
        
        tree = ttk.Treeview(tab, columns=('ID', 'Должность', 'Оклад', '%'), show='headings', height=10)
        tree.pack(fill='both', expand=True, padx=10, pady=5)
        for col, w in [('ID', 40), ('Должность', 200), ('Оклад', 100), ('%', 100)]:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center' if col != 'Должность' else 'w')
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            self.cursor.execute("SELECT id, name, salary_base, bonus_percent FROM job_titles ORDER BY id")
            for row in self.cursor.fetchall():
                tree.insert('', 'end', values=row)
        
        form = tk.Frame(tab)
        form.pack(fill='x', padx=10, pady=5)
        name_e = ttk.Entry(form, width=20)
        name_e.pack(side='left', padx=2)
        sal_e = ttk.Entry(form, width=8)
        sal_e.pack(side='left', padx=2)
        pct_e = ttk.Entry(form, width=5)
        pct_e.pack(side='left', padx=2)
        
        def add():
            try:
                self.cursor.execute("INSERT INTO job_titles (name, salary_base, bonus_percent) VALUES (?, ?, ?)",
                                   (name_e.get(), float(sal_e.get()), float(pct_e.get())))
                self.conn.commit()
                refresh()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверные числа")
        
        def edit():
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel[0])
            try:
                self.cursor.execute("UPDATE job_titles SET name=?, salary_base=?, bonus_percent=? WHERE id=?",
                                   (name_e.get() or item['values'][1],
                                    float(sal_e.get() or item['values'][2]),
                                    float(pct_e.get() or item['values'][3]), item['values'][0]))
                self.conn.commit()
                refresh()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверные числа")
        
        btn = tk.Frame(tab)
        btn.pack(pady=5)
        ttk.Button(btn, text="➕", command=add).pack(side='left', padx=2)
        ttk.Button(btn, text="✏️", command=edit).pack(side='left', padx=2)
        refresh()
    
    # ============================================================
    # ВКЛАДКА: СТОЛИКИ
    # ============================================================
    def build_tables_tab(self, notebook):
        tab = tk.Frame(notebook, bg='#fafafa')
        notebook.add(tab, text="🪑 Столики")
        
        tree = ttk.Treeview(tab, columns=('ID', 'Номер', 'Мест'), show='headings', height=10)
        tree.pack(fill='both', expand=True, padx=10, pady=5)
        for col, w in [('ID', 50), ('Номер', 100), ('Мест', 100)]:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center')
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            self.cursor.execute("SELECT id, table_number, capacity FROM tables_cafe ORDER BY table_number")
            for row in self.cursor.fetchall():
                tree.insert('', 'end', values=row)
        
        form = tk.Frame(tab)
        form.pack(fill='x', padx=10, pady=5)
        num_e = ttk.Entry(form, width=5)
        num_e.pack(side='left', padx=2)
        cap_e = ttk.Entry(form, width=5)
        cap_e.pack(side='left', padx=2)
        
        def add():
            try:
                self.cursor.execute("INSERT OR IGNORE INTO tables_cafe (table_number, capacity) VALUES (?, ?)",
                                   (int(num_e.get()), int(cap_e.get())))
                self.conn.commit()
                refresh()
                if self.load_tables: self.load_tables()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверные числа")
        
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno("Удалить", "Удалить столик?"):
                self.cursor.execute("DELETE FROM tables_cafe WHERE id=?", (tree.item(sel[0])['values'][0],))
                self.conn.commit()
                refresh()
                if self.load_tables: self.load_tables()
        
        ttk.Button(form, text="➕", command=add).pack(side='left', padx=2)
        ttk.Button(tab, text="🗑️ Удалить", command=delete).pack(pady=5)
        refresh()
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()