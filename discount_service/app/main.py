from pydantic import BaseModel

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

    if req.promo_code and req.promo_code.upper() in PROMO_CODES:
        percent = PROMO_CODES[req.promo_code.upper()]
        reason = f"Промокод {req.promo_code.upper()}"
    elif req.quantity >= 10:
        percent = 10
        reason = "Оптовая скидка от 10 шт"
    elif req.quantity >= 5:
        percent = 5
        reason = "Оптовая скидка от 5 шт"

    return {"percent": percent, "reason": reason}