"""Сервис скидок"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Discount Service", version="1.0.0")

# Промокоды
PROMO_CODES = {
    "STUDENT10": 10,
    "COFFEE20": 20,
    "BIRTHDAY": 15,
}


class DiscountRequest(BaseModel):
    dish_id: int
    quantity: int
    price_per_unit: float
    promo_code: str | None = None


@app.post("/discounts/calculate")
def calculate_discount(req: DiscountRequest):
    percent = 0
    reason = "Скидка не применена"

    # Проверка промокода
    if req.promo_code and req.promo_code.upper() in PROMO_CODES:
        percent = PROMO_CODES[req.promo_code.upper()]
        reason = f"Промокод {req.promo_code.upper()}: скидка {percent}%"

    # Оптовая скидка (от 5 штук)
    elif req.quantity >= 5:
        percent = 5
        reason = f"Оптовая скидка при заказе от 5 шт: {percent}%"

    # Большой заказ (от 10 штук)
    elif req.quantity >= 10:
        percent = 10
        reason = f"Оптовая скидка при заказе от 10 шт: {percent}%"

    return {
        "percent": percent,
        "reason": reason,
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "discount-service"}