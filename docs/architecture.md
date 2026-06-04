# Архитектура системы

## Десктоп-приложение
```mermaid
graph TD
    Main[main_window.py<br/>Официант] --> DB[database.py]
    Kitchen[kitchen_window.py<br/>Кухня] --> DB
    Stock[stock_window.py<br/>Склад] --> DB
    Reports[reports_window.py<br/>Отчёты] --> DB
    Orders[orders_window.py<br/>Заказы] --> DB
    Staff[staff_window.py<br/>Зарплата] --> DB
    Admin[admin_panel.py<br/>Администрирование] --> DB
    DB --> SQLite[(cafe.db<br/>SQLite)]
```
```mermaid
graph LR
    Browser[Браузер] --> Menu[menu-service<br/>:8001]
    Browser --> Order[order-service<br/>:8002]
    Menu --> PG[(PostgreSQL<br/>:5432)]
    Order --> PG
    Order -.-> Menu
```
```mermaid
graph TD
    subgraph UI[Интерфейс]
        Tk[Tkinter Windows]
        Swagger[FastAPI Swagger]
    end
    
    subgraph Logic[Бизнес-логика]
        DB[database.py]
        Models[models.py]
    end
    
    subgraph Storage[Хранилище]
        SQLite[(SQLite)]
        PG2[(PostgreSQL)]
    end
    
    UI --> Logic
    Logic --> Storage
```
## Микросервисы (Docker)

| Сервис | Порт | Назначение |
| :--- | :---: | :--- |
| menu-service | 8001 | Меню, склад |
| order-service | 8002 | Заказы, кухня |
| db | 5432 | PostgreSQL |