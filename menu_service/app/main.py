"""Сервис меню и склада"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI(title="Menu Service", version="1.0.0")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "cafe"),
    "password": os.getenv("DB_PASS", "cafe123"),
    "dbname": os.getenv("DB_NAME", "cafe_db"),
}


def get_db():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id_dish SERIAL PRIMARY KEY,
            name_of_dish VARCHAR(200) NOT NULL,
            price REAL NOT NULL,
            cooking_time INTEGER DEFAULT 10,
            is_available BOOLEAN DEFAULT TRUE
        );
        
        CREATE TABLE IF NOT EXISTS products (
            id_product SERIAL PRIMARY KEY,
            name_of_product VARCHAR(200) NOT NULL,
            unit VARCHAR(20) NOT NULL,
            quantity_at_storage REAL DEFAULT 0,
            cost_per_unit REAL DEFAULT 0
        );
    ''')
    
    # Добавляем данные, если таблицы пустые
    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        cur.execute('''
            INSERT INTO menu (name_of_dish, price, cooking_time) VALUES
            ('Цезарь с курицей', 280.00, 10),
            ('Борщ', 220.00, 15),
            ('Стейк из говядины', 450.00, 20),
            ('Американо', 120.00, 3),
            ('Капучино', 150.00, 3),
            ('Чизкейк', 200.00, 3);
        ''')
    
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        cur.execute('''
            INSERT INTO products (name_of_product, unit, quantity_at_storage, cost_per_unit) VALUES
            ('Куриное филе', 'кг', 5.0, 280.00),
            ('Говядина', 'кг', 3.0, 600.00),
            ('Кофе зерновой', 'кг', 1.0, 1200.00),
            ('Молоко', 'л', 10.0, 70.00);
        ''')
    
    conn.commit()
    conn.close()

# Вызываем при старте
@app.on_event("startup")
def startup():
    init_db()


@app.get("/menu")
def get_menu():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id_dish, name_of_dish, price, cooking_time "
        "FROM menu WHERE is_available = true"
    )
    dishes = [
        {"id": r[0], "name": r[1], "price": r[2], "cooking_time": r[3]}
        for r in cur.fetchall()
    ]
    conn.close()
    return dishes


@app.get("/stock")
def get_stock():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id_product, name_of_product, unit, quantity_at_storage "
        "FROM products ORDER BY quantity_at_storage ASC"
    )
    stock = [
        {"id": r[0], "name": r[1], "unit": r[2], "quantity": r[3]}
        for r in cur.fetchall()
    ]
    conn.close()
    return stock


@app.get("/health")
def health():
    return {"status": "ok", "service": "menu-service"}