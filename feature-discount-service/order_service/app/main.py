"""Сервис заказов"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="Order Service", version="1.0.0")

MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://menu-service:8000")
DISCOUNT_SERVICE_URL = os.getenv("DISCOUNT_SERVICE_URL", "http://discount-service:8000")


class OrderItem(BaseModel):
    dish_id: int
    quantity: int


class CreateOrder(BaseModel):
    table_num: int
    employee_id: int
    promo_code: str | None = None
    items: list[OrderItem]


@app.post("/orders")
async def create_order(req: CreateOrder):
    total_before = 0
    total_after = 0
    details = []

    async with httpx.AsyncClient() as client:
        # 1. Получить меню
        menu_resp = await client.get(f"{MENU_SERVICE_URL}/menu")
        menu = menu_resp.json()

        for item in req.items:
            dish = next((d for d in menu if d["id"] == item.dish_id), None)
            if not dish:
                raise HTTPException(404, f"Блюдо {item.dish_id} не найдено")

            price = dish["price"]
            item_total = price * item.quantity

            # 2. Запросить скидку
            disc_resp = await client.post(
                f"{DISCOUNT_SERVICE_URL}/discounts/calculate",
                json={
                    "dish_id": item.dish_id,
                    "quantity": item.quantity,
                    "price_per_unit": price,
                    "promo_code": req.promo_code,
                },
            )
            disc = disc_resp.json()
            percent = disc["percent"]
            discount = item_total * percent / 100
            final = item_total - discount

            total_before += item_total
            total_after += final
            details.append({
                "dish_id": item.dish_id,
                "dish_name": dish["name"],
                "quantity": item.quantity,
                "price_per_unit": price,
                "total_before_discount": item_total,
                "discount_percent": percent,
                "discount_amount": discount,
                "total_after_discount": final,
                "discount_reason": disc["reason"],
            })

    return {
        "order_id": 1,
        "total_before_discount": total_before,
        "total_after_discount": total_after,
        "details": details,
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "order-service"}