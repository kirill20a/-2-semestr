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


class OrderItem(BaseModel):
    dish_id: int
    quantity: int


class CreateOrder(BaseModel):
    table_num: int
    employee_id: int
    items: list[OrderItem]


@app.post("/orders")
async def create_order(req: CreateOrder):
    """Создать заказ с проверкой меню"""
    # Проверяем наличие блюд через menu-service
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{MENU_SERVICE_URL}/menu")
        menu = resp.json()
    
    menu_ids = {d["id"] for d in menu}
    for item in req.items:
        if item.dish_id not in menu_ids:
            raise HTTPException(404, f"Блюдо {item.dish_id} не найдено в меню")
    
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
    """Очередь кухни"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT o.id_order, o.table_num, m.name_of_dish, oi.quantity "
        "FROM order_items oi "
        "JOIN orders o ON oi.id_order = o.id_order "
        "JOIN menu m ON oi.id_dish = m.id_dish "
        "WHERE oi.ready_status = 0 AND o.status IN ('Готовится') "
        "ORDER BY o.created_at"
    )
    queue = [
        {"order_id": r[0], "table": r[1], "dish": r[2], "quantity": r[3]}
        for r in cur.fetchall()
    ]
    conn.close()
    return queue


@app.get("/health")
def health():
    return {"status": "ok", "service": "order-service"}