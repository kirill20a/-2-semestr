"""
Централизованное хранение настроек:
- Пути к файлам
- Настройки БД
- Параметры UI
"""
import os
from pathlib import Path


class Config:
    
    # Пути
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    DB_PATH = DATA_DIR / 'cafe.db'
    
    # Настройки БД
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    
    # Настройки UI
    APP_TITLE = "Кафе «Вкусное место»"
    APP_WIDTH = 750
    APP_HEIGHT = 650
    
    # Цвета
    COLOR_PRIMARY = '#4a7c59'
    COLOR_BACKGROUND = '#f0f0f0'
    COLOR_LIGHT = '#fafafa'
    
    # Шрифты
    FONT_TITLE = ('Arial', 16, 'bold')
    FONT_NORMAL = ('Arial', 11)
    FONT_MONO = ('Consolas', 10)
    
    @classmethod
    def ensure_dirs(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


# Глобальный экземпляр конфигурации
config = Config()