"""Сервис заказов и кухни"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import httpx
import os

app = FastAPI(title="Order Service", version="1.0.0")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "cafe"),
    "password": os.getenv("DB_PASS", "cafe123"),
    "dbname": os.getenv("DB_NAME", "cafe_db"),
}

MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://menu-service:8000")


def get_db():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Создание таблиц при первом запуске"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id_order SERIAL PRIMARY KEY,
            table_num INTEGER NOT NULL,
            id_employee INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            status VARCHAR(20) DEFAULT 'Открыт'
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id_item SERIAL PRIMARY KEY,
            id_order INTEGER NOT NULL REFERENCES orders(id_order),
            id_dish INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            ready_status BOOLEAN DEFAULT FALSE
        );
    ''')
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


class OrderItem(BaseModel):
    dish_id: int
    quantity: int


class CreateOrder(BaseModel):
    table_num: int
    employee_id: int
    items: list[OrderItem]


@app.post("/orders")
async def create_order(req: CreateOrder):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (table_num, id_employee, status) "
        "VALUES (%s, %s, 'Готовится') RETURNING id_order",
        (req.table_num, req.employee_id),
    )
    order_id = cur.fetchone()[0]
    
    for item in req.items:
        cur.execute(
            "INSERT INTO order_items (id_order, id_dish, quantity) "
            "VALUES (%s, %s, %s)",
            (order_id, item.dish_id, item.quantity),
        )
    
    conn.commit()
    conn.close()
    return {"order_id": order_id}


@app.get("/kitchen")
def kitchen_queue():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT o.id_order, o.table_num, oi.id_dish, oi.quantity "
        "FROM order_items oi "
        "JOIN orders o ON oi.id_order = o.id_order "
        "WHERE oi.ready_status = FALSE AND o.status = 'Готовится' "
        "ORDER BY o.created_at"
    )
    queue = [
        {"order_id": r[0], "table": r[1], "dish_id": r[2], "quantity": r[3]}
        for r in cur.fetchall()
    ]
    conn.close()
    return queue


@app.get("/health")
def health():
    return {"status": "ok", "service": "order-service"}
