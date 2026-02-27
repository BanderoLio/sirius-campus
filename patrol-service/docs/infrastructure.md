# Инфраструктура patrol-service

## Окружение

| Параметр            | Значение                                      |
|---------------------|-----------------------------------------------|
| REST-порт           | 8002                                          |
| gRPC-порт           | 50052                                         |
| База данных         | PostgreSQL 15+ (patrol_db, порт 5433 в dev)   |
| Внешние gRPC-зависимости | auth-service (50051), application-service (50055) |

## Переменные окружения

| Переменная               | Обязательная | Пример значения                                                     | Описание                              |
|--------------------------|:------------:|---------------------------------------------------------------------|---------------------------------------|
| DATABASE_URL             | Да           | postgresql+asyncpg://campus:secret@postgres-patrol:5432/patrol_db  | DSN подключения к БД                  |
| AUTH_GRPC_HOST           | Да           | auth-service                                                        | Хост auth-service (gRPC)              |
| AUTH_GRPC_PORT           | Да           | 50051                                                               | Порт auth-service (gRPC)              |
| APPLICATION_GRPC_HOST    | Да           | application-service                                                 | Хост application-service (gRPC)       |
| APPLICATION_GRPC_PORT    | Да           | 50055                                                               | Порт application-service (gRPC)       |
| GRPC_TIMEOUT_SECONDS     | Нет          | 5                                                                   | Таймаут gRPC-вызовов (сек.)           |
| GRPC_MAX_RETRIES         | Нет          | 3                                                                   | Максимальное число ретраев gRPC       |
| LOG_LEVEL                | Нет          | INFO                                                                | Уровень логирования                   |
| LOKI_URL                 | Нет          | http://loki:3100                                                    | URL Loki для отправки логов           |
| JWT_SECRET_KEY           | Да           | supersecretkey                                                      | Секрет для первичной проверки JWT     |
| ENVIRONMENT              | Нет          | development                                                         | Окружение (development/production)    |

## Dockerfile

```dockerfile
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base AS deps
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only main

FROM base AS runtime
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY . .

EXPOSE 8002 50052

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

## Docker Compose (фрагмент для patrol-service)

```yaml
patrol-service:
  build: ./patrol-service
  ports:
    - '8002:8002'
    - '50052:50052'
  env_file: ./patrol-service/.env
  environment:
    - DATABASE_URL=postgresql+asyncpg://campus:campus_secret@postgres-patrol:5432/patrol_db
    - AUTH_GRPC_HOST=auth-service
    - AUTH_GRPC_PORT=50051
    - APPLICATION_GRPC_HOST=application-service
    - APPLICATION_GRPC_PORT=50055
    - LOKI_URL=http://loki:3100
    - ENVIRONMENT=development
  depends_on:
    - postgres-patrol
    - auth-service
    - application-service
    - loki

postgres-patrol:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: campus
    POSTGRES_PASSWORD: campus_secret
    POSTGRES_DB: patrol_db
  ports:
    - '5433:5432'
  volumes:
    - pg_patrol_data:/var/lib/postgresql/data
```

## Миграции

Миграции выполняются через Alembic. Запуск при старте контейнера:

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8002"]
```

## Мониторинг и логирование

| Компонент  | Назначение                          | Порт  |
|------------|-------------------------------------|-------|
| Prometheus | Сбор метрик (`/metrics`)            | 9090  |
| Grafana    | Дашборды метрик и логов             | 3000  |
| Loki       | Агрегация структурированных логов   | 3100  |

Метрики экспортируются через эндпоинт `GET /metrics` (prometheus-fastapi-instrumentator).  
Логирование — structlog, формат JSON, отправка в Loki через HTTP.  
Все запросы логируются с полями `trace_id`, `correlation_id`, `method`, `path`, `status_code`, `duration_ms`.

## Трассировка

Каждый входящий REST-запрос:
- Читает заголовок `X-Trace-ID` (если отсутствует — генерирует новый UUID).
- Читает заголовок `X-Correlation-ID` (если отсутствует — генерирует новый UUID).
- Проставляет оба заголовка во все исходящие gRPC-вызовы через metadata.
- Возвращает оба заголовка в ответе.