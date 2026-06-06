"""Сервис скидок"""
from fastapi import FastAPI

app = FastAPI(title="Discount Service", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "discount-service"}