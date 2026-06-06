"""Сервис заказов"""
from fastapi import FastAPI
import os
from pydantic import BaseModel
import httpx

app = FastAPI(title="Order Service", version="1.0.0")

MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://menu-service:8000")
DISCOUNT_SERVICE_URL = os.getenv("DISCOUNT_SERVICE_URL", "http://discount-service:8000")


class OrderItem(BaseModel):
    dish_id: int
    quantity: int

class CreateOrder(BaseModel):
    table_num: int
    employee_id: int
    items: list[OrderItem]

@app.post("/orders")
async def create_order(req: CreateOrder):
    async with httpx.AsyncClient() as client:
        menu_resp = await client.get(f"{MENU_SERVICE_URL}/menu")
        menu = menu_resp.json()
    return {"menu": menu, "items": req.items}

@app.get("/health")
def health():
    return {"status": "ok", "service": "order-service"}