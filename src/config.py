"""Конфигурация приложения"""
import os

DB_NAME = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'cafe.db'
)