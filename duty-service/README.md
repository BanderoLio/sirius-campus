# Duty Service

Микросервис управления дежурствами в Кампусе Сириус.

## Структура проекта

```
duty-service/
├── src/
│   ├── main.py              # Точка входа FastAPI приложения
│   ├── config.py            # Конфигурация сервиса
│   ├── database/
│   │   ├── __init__.py      # Инициализация БД
│   │   └── models.py        # SQLAlchemy модели
│   ├── schemas/             # Pydantic схемы для валидации
│   └── routes/              # API эндпоинты
├── requirements.txt         # Python зависимости
├── Dockerfile              # Образ Docker
├── docker-compose.yml      # Оркестрация контейнеров
├── COMMENTS.md             # Подробные комментарии к коду
└── README.md               # Этот файл
```

## Технологический стек

- **Python 3.11+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM (async)
- **PostgreSQL 15** - база данных
- **asyncpg** - драйвер для PostgreSQL
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер

## Быстрый старт

### Запуск с Docker Compose

```bash
docker-compose up --build
```

Сервис будет доступен по адресу:
- API: http://localhost:8003
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

### Остановка

```bash
docker-compose down
```

### Остановка с удалением данных

```bash
docker-compose down -v
```

## API Endpoints

### Расписания дежурств

- `GET /api/v1/duties/schedules` - список расписаний
- `POST /api/v1/duties/schedules` - создать расписание
- `GET /api/v1/duties/schedules/{id}` - получить расписание
- `PUT /api/v1/duties/schedules/{id}` - обновить расписание
- `PATCH /api/v1/duties/schedules/{id}` - изменить статус
- `DELETE /api/v1/duties/schedules/{id}` - удалить расписание

### Отчёты о дежурствах

- `GET /api/v1/duties/reports` - список отчётов
- `POST /api/v1/duties/reports` - создать отчёт
- `GET /api/v1/duties/reports/{id}` - получить отчёт с фотографиями
- `PUT /api/v1/duties/reports/{id}` - обновить отчёт
- `PATCH /api/v1/duties/reports/{id}` - изменить статус
- `DELETE /api/v1/duties/reports/{id}` - удалить отчёт

### Фотографии в отчётах

- `POST /api/v1/duties/reports/{report_id}/images` - добавить фотографию
- `DELETE /api/v1/duties/reports/{report_id}/images/{image_id}` - удалить фотографию

### Категории фотографий

- `GET /api/v1/duties/categories` - список категорий

### Health Check

- `GET /health` - проверка состояния сервиса

## Разработка

### Локальный запуск без Docker

1. Создать виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Запустить PostgreSQL (например, через Docker):
```bash
docker run --name duty-db -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -e POSTGRES_DB=duty_db -p 5433:5432 -d postgres:15-alpine
```

4. Настроить переменные окружения в `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/duty_db
SERVICE_PORT=8003
ENVIRONMENT=development
LOG_LEVEL=INFO
```

5. Запустить сервис:
```bash
uvicorn src.main:app --reload --port 8003
```

## Документация

Подробные комментарии к коду и архитектуре находятся в файле [COMMENTS.md](COMMENTS.md).

## База данных

Сервис автоматически создаёт все необходимые таблицы при запуске.

### Таблицы:
- `duty_schedules` - расписания дежурств
- `duty_reports` - отчёты о выполнении
- `duty_report_images` - фотографии в отчётах
- `duty_categories` - категории фотографий

## Порты

- **8003** - REST API (HTTP)
- **50053** - gRPC (зарезервирован)
- **5433** - PostgreSQL (внешний порт)

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| DATABASE_URL | URL подключения к PostgreSQL | postgresql+asyncpg://user:password@db:5432/duty_db |
| SERVICE_PORT | Порт REST API | 8003 |
| ENVIRONMENT | Окружение (development/production) | development |
| LOG_LEVEL | Уровень логирования | INFO |

## Мониторинг

Health check endpoint доступен по адресу `/health` и возвращает:
```json
{
  "status": "healthy",
  "service": "duty-service",
  "version": "1.0.0"
}
```

Docker использует этот endpoint для проверки готовности контейнера.
