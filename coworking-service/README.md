# Coworking Service

Микросервис управления коворкингами и бронированиями (Кампус Сириус).

**Стек:** Python 3.11, FastAPI, SQLAlchemy 2, asyncpg, Alembic, gRPC (авторизация).

## Быстрый старт

### 1. PostgreSQL

```bash
docker run -d --name postgres-coworking \
  -e POSTGRES_USER=campus \
  -e POSTGRES_PASSWORD=campus_secret \
  -e POSTGRES_DB=coworking_db \
  -p 5437:5432 \
  postgres:15
```

> Если контейнер уже существует: `docker start postgres-coworking`

### 2. Backend

```bash
cd coworking-service
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8004
```

API доступен на http://localhost:8004

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI доступен на http://localhost:5173

> По умолчанию Vite проксирует `/api` на `http://localhost:8080` (gateway).
> Для работы без gateway измените `target` в `frontend/vite.config.ts` на `http://localhost:8004`.

## Переменные окружения

Файл `coworking-service/.env`:

| Переменная | Значение по умолчанию | Описание |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://campus:campus_secret@localhost:5437/coworking_db` | Подключение к PostgreSQL |
| `AUTH_GRPC_URL` | `localhost:50051` | Адрес gRPC-сервиса авторизации |
| `APP_NAME` | `coworking-service` | Имя приложения (для логов) |
| `LOG_LEVEL` | `INFO` | Уровень логирования |
| `LOKI_URL` | `http://localhost:3100` | URL Loki для отправки логов |

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/v1/coworkings` | Список коворкингов (фильтры: building, entrance, available) |
| GET | `/api/v1/coworkings/{id}` | Коворкинг по ID |
| POST | `/api/v1/bookings` | Создать бронирование |
| GET | `/api/v1/bookings` | Все бронирования (админ) |
| GET | `/api/v1/bookings/my` | Бронирования текущего пользователя |
| GET | `/api/v1/bookings/active` | Активные бронирования |
| GET | `/api/v1/bookings/history` | История бронирований |
| PATCH | `/api/v1/bookings/{id}/confirm` | Подтвердить бронирование |
| PATCH | `/api/v1/bookings/{id}/close` | Закрыть бронирование |
| PATCH | `/api/v1/bookings/{id}/cancel` | Отменить бронирование |

Авторизация — заголовок `Authorization: Bearer <token>`.

Swagger UI: http://localhost:8004/docs

## Структура

```
coworking-service/
├── alembic/              # Миграции БД
├── src/
│   ├── api/v1/           # Роутеры (coworkings, bookings)
│   ├── models/           # SQLAlchemy-модели
│   ├── repositories/     # Слой доступа к данным
│   ├── services/         # Бизнес-логика
│   ├── schemas/          # Pydantic-схемы
│   ├── config.py         # Настройки приложения
│   ├── database.py       # Подключение к БД
│   └── main.py           # Точка входа FastAPI
├── tests/
├── pyproject.toml
├── requirements.txt
├── Dockerfile
└── .env
```
