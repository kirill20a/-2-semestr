# Networking Notes

## Локальный запуск
Все на хосте: `http://127.0.0.1:8001`, `http://127.0.0.1:8002`, `http://127.0.0.1:8003`.

## Ошибка: 127.0.0.1 в контейнере
Внутри контейнера `127.0.0.1` = сам контейнер. Connection Refused.

## Успех: имена сервисов
В Docker: `http://menu-service:8000`, `http://discount-service:8000`.

## Доступ с хоста
С хоста: `http://localhost:8001`. Из контейнера к хосту: `host.docker.internal`.