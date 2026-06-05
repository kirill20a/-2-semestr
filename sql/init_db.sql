PRAGMA foreign_keys = OFF;

CREATE TABLE IF NOT EXISTS tables_cafe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number INTEGER NOT NULL UNIQUE,
    capacity INTEGER DEFAULT 4,
    is_occupied INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS job_titles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    salary_base REAL DEFAULT 0,
    bonus_percent REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    id_job_title INTEGER NOT NULL,
    FOREIGN KEY (id_job_title) REFERENCES job_titles(id)
);

CREATE TABLE IF NOT EXISTS categories (
    id_category INTEGER PRIMARY KEY AUTOINCREMENT,
    name_category TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS menu (
    id_dish INTEGER PRIMARY KEY AUTOINCREMENT,
    name_of_dish TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    id_category INTEGER NOT NULL,
    cooking_time INTEGER DEFAULT 10,
    is_available INTEGER DEFAULT 1,
    FOREIGN KEY (id_category) REFERENCES categories(id_category)
);

CREATE TABLE IF NOT EXISTS products (
    id_product INTEGER PRIMARY KEY AUTOINCREMENT,
    name_of_product TEXT NOT NULL,
    unit TEXT NOT NULL,
    quantity_at_storage REAL NOT NULL DEFAULT 0,
    cost_per_unit REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dish_composition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_dish INTEGER NOT NULL,
    id_product INTEGER NOT NULL,
    quantity REAL NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (id_dish) REFERENCES menu(id_dish),
    FOREIGN KEY (id_product) REFERENCES products(id_product)
);

CREATE TABLE IF NOT EXISTS orders (
    id_order INTEGER PRIMARY KEY AUTOINCREMENT,
    table_num INTEGER NOT NULL,
    id_employee INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    status TEXT DEFAULT 'Открыт',
    FOREIGN KEY (id_employee) REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id_item INTEGER PRIMARY KEY AUTOINCREMENT,
    id_order INTEGER NOT NULL,
    id_dish INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    ready_status INTEGER DEFAULT 0,
    FOREIGN KEY (id_order) REFERENCES orders(id_order),
    FOREIGN KEY (id_dish) REFERENCES menu(id_dish)
);

PRAGMA foreign_keys = ON;