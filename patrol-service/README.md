# Patrol Service

Микросервис обходов проекта «Кампус Сириус».

## Описание

Управляет сеансами обхода подъездов и записями проверки студентов.

### Функционал:
- Создание сеансов обхода для указанного корпуса и подъезда
- Автоматическое создание записей для несовершеннолетних студентов
- Интеграция с auth-service для получения списка студентов
- Интеграция с application-service для получения одобренных заявлений на выход
- Отметка присутствия/отсутствия студентов
- Завершение обхода

## Технологии

- Python 3.11+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL 15+
- Alembic (миграции)
- gRPC (клиенты для auth-service и application-service)
- structlog (логирование)
- Prometheus (метрики)

## Структура проекта

```
patrol-service/
├── alembic/                 # Миграции базы данных
│   ├── versions/
│   └── env.py
├── proto/                   # Protobuf определения
├── src/
│   ├── api/                 # REST API эндпоинты
│   │   └── v1/patrols/
│   ├── config/              # Конфигурация
│   ├── constants/           # Константы и коды ошибок
│   ├── domain/              # Доменные исключения
│   ├── exceptions/          # Обработчики исключений
│   ├── grpc_clients/        # gRPC клиенты
│   ├── middleware/          # Middleware (tracing)
│   ├── models/              # SQLAlchemy модели
│   ├── repositories/        # Репозитории для работы с БД
│   └── services/            # Бизнес-логика
├── tests/                   # Тесты
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## API Эндпоинты

Базовый URL: `http://localhost:8002/api/v1`

| Метод  | Путь                                    | Описание                                   |
|--------|-----------------------------------------|-------------------------------------------|
| GET    | /patrols                                | Список обходов с пагинацией и фильтрацией |
| POST   | /patrols                                | Создать новый сеанс обхода                |
| GET    | /patrols/{patrolId}                     | Получить полное состояние обхода          |
| PATCH  | /patrols/{patrolId}                     | Завершить обход                           |
| DELETE | /patrols/{patrolId}                     | Удалить сеанс обхода                      |
| GET    | /patrols/{patrolId}/{patrolEntryId}     | Получить запись проверки студента         |
| PATCH  | /patrols/{patrolId}/{patrolEntryId}     | Обновить запись проверки студента         |

## Запуск

### Локальная разработка

```bash
# Установка зависимостей
poetry install

# Применение миграций
alembic upgrade head

# Запуск сервера
uvicorn src.main:app --host 0.0.0.0 --port 8002
```

### Docker

```bash
docker build -t patrol-service .
docker run -p 8002:8002 patrol-service
```

### docker-compose
```bash
docker-compose up --build patrol-service
```

## Переменные окружения

| Переменная               | Обязательная | Описание                              |
|--------------------------|:------------:|---------------------------------------|
| DATABASE_URL             | Да           | DSN подключения к БД                  |
| AUTH_GRPC_HOST           | Да           | Хост auth-service (gRPC)              |
| AUTH_GRPC_PORT           | Да           | Порт auth-service (gRPC)              |
| APPLICATION_GRPC_HOST    | Да           | Хост application-service (gRPC)       |
| APPLICATION_GRPC_PORT    | Да           | Порт application-service (gRPC)       |
| JWT_SECRET_KEY           | Да           | Секрет для проверки JWT               |
| LOG_LEVEL                | Нет          | Уровень логирования (default: INFO)   |
| LOKI_URL                 | Нет          | URL Loki для отправки логов           |
| ENVIRONMENT              | Нет          | Окружение (development/production)    |

## Тесты

```bash
# Запуск тестов
pytest

# С покрытием
pytest --cov=src
```

## Health Check

- `GET /health/liveness` - проверка живучести сервиса
- `GET /health/readiness` - проверка готовности (включая БД)
- `GET /metrics` - метрики Prometheus

## Фронтенд

Для patrol-service реализован фронтенд в директории `frontend/`:

### Запуск

```bash
cd frontend
npm install
npm run dev
```

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Настройте переменные окружения:

```bash
VITE_API_BASE_URL=http://localhost:8000          # Основной API
VITE_PATROL_API_BASE_URL=http://localhost:8002    # Patrol Service API (опционально)
```

#### Доступные скрипты

- `npm run dev` — запуск dev-сервера
- `npm run build` — сборка для продакшена
- `npm run preview` — preview сборки
- `npm run lint` — проверка линтером
- `npm run format` — форматирование кода

### Маршруты

- `/patrols` — список всех обходов с фильтрами
- `/patrols/new` — создание нового обхода
- `/patrols/:id` — детали обхода и управление записями студентов

### Структура файлов

```
frontend/src/
├── api/patrols.api.ts       # API-клиент для обходов
├── stores/patrols.store.ts  # Pinia store для управления состоянием
├── types/patrols.types.ts    # TypeScript типы
└── views/patrols/
    ├── PatrolsListView.vue  # Список обходов
    ├── PatrolNewView.vue    # Создание нового обхода
    └── PatrolDetailView.vue # Детали обхода и проверка студентов
```

### Функциональность

1. **Список обходов** — просмотр всех обходов с фильтрацией по дате, корпусу, подъезду и статусу
2. **Создание обхода** — начало нового сеанса обхода с указанием даты, корпуса и подъезда
3. **Детали обхода** — просмотр списка студентов, отметка присутствия/отсутствия
4. **Завершение обхода** — перевод обхода в статус "Завершён"
