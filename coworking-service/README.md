# Coworking Service

Микросервис управления коворкингами и бронированиями (Кампус Сириус).

## Быстрый старт

### 1. Все контейнеры (Docker Compose): Backend + Frontend

Запуск PostgreSQL, backend (coworking-service) и frontend одной командой:

```bash
cd coworking-service
docker compose up -d
```

При первом запуске примените миграции:

```bash
docker compose run --rm coworking-service alembic upgrade head
```

- **Backend API:** http://localhost:8004  
- **Frontend UI:** http://localhost:5173  
- **PostgreSQL:** порт 5437 (localhost:5437)

Frontend в контейнере проксирует запросы `/api` на backend; для этого в сервис передаётся `VITE_API_TARGET=http://coworking-service:8004`.

> Остановить: `docker compose down`. Данные БД сохраняются в volume `pg_coworking_data`.
> Полный сброс БД (удаление volume): `docker compose down -v`, затем `docker compose up -d` и `docker compose run --rm coworking-service alembic upgrade head`.

### 2. Backend (без Docker)

**PostgreSQL** (если не используете docker-compose):

```bash
docker run -d --name postgres-coworking \
  -e POSTGRES_USER=campus \
  -e POSTGRES_PASSWORD=campus_secret \
  -e POSTGRES_DB=coworking_db \
  -p 5437:5432 \
  postgres:15
```

> Если контейнер уже существует: `docker start postgres-coworking`

**Backend:**

```bash
cd coworking-service
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8004
```

API доступен на http://localhost:8004

### 3. Frontend (локально, без Docker)

```bash
cd frontend
npm install
npm run dev
```

UI доступен на http://localhost:5173

> По умолчанию Vite проксирует `/api` на `http://localhost:8004` (coworking-service).  
> Целевой адрес API задаётся переменной `VITE_API_TARGET` (в Docker — `http://coworking-service:8004`).
