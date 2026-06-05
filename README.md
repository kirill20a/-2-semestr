# 🍽️ Cafe IS — Информационная система кафе

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

Система автоматизации небольшого кафе с управлением заказами, кухней, складом и персоналом.

## ✨ Возможности

- 📋 Управление столиками и заказами
- 👨‍🍳 Экран кухни с очередью заказов
- 📦 Складской учёт продуктов
- 📊 Отчёты по выручке и популярности блюд
- 👥 Расчёт зарплаты с KPI

# 🍽️ Cafe IS — Информационная система кафе

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)

## 🚀 Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/kirill20a/-2-semestr.git
cd CAFE

# Установить зависимости
make setup

# Запустить десктопное приложение
make run
```

## 🐳 Docker

```bash
make compose-up
# → http://localhost:8001/docs — Menu Service
# → http://localhost:8002/docs — Order Service
```

## 🧪 Тесты

```bash
make test
make coverage
```

## 📖 Документация

```bash
make docs-serve
# → http://localhost:8000
```

## 📦 Установка пакета

```bash
pip install --index-url https://test.pypi.org/simple/ cafe-is
```
## Публикация в PyPI

Пакет опубликован в TestPyPI: https://test.pypi.org/project/cafe-is/

Установка:
```bash
pip install --index-url https://test.pypi.org/simple/ cafe-is

## 👥 Авторы

- Агаев Кирилл — разработка БД , десктоп-приложения , Docker, PyPI
- Асанов Денис — интерфейс, документация, тестирование
