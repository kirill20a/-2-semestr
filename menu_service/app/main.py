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


class StockUpdate(BaseModel):
    product_id: int
    quantity: float


@app.get("/menu")
def get_menu():
    """Получить меню"""
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
    """Остатки на складе"""
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