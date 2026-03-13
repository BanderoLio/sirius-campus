# ТЗ-0: API-контракты и единые правила написания кода

## Содержание

1. [Общие сведения](#1-общие-сведения)
2. [Архитектура проекта](#2-архитектура-проекта)
3. [Структура микросервиса](#3-структура-микросервиса)
4. [API-контракты (REST)](#4-api-контракты-rest)
5. [gRPC-контракты (межсервисное взаимодействие)](#5-grpc-контракты-межсервисное-взаимодействие)
6. [Аутентификация и авторизация](#6-аутентификация-и-авторизация)
7. [Docker и деплой](#7-docker-и-деплой)
8. [Версионирование и Git](#8-версионирование-и-git)

> **Примечание:** Детальные требования к написанию кода, обработке ошибок, работе с БД, логированию и тестированию см. в [PYTHON-GUIDELINES.md](./PYTHON-GUIDELINES.md)

---

## 1. Общие сведения

### 1.1 Название проекта

**Кампус Сириус** — веб-приложение для автоматизации работы воспитателей и улучшения пользовательского опыта студентов Колледжа Сириус.

### 1.2 Стек технологий

| Компонент             | Технология                       |
| --------------------- | -------------------------------- |
| Язык                  | Python 3.11+                     |
| Web-фреймворк         | FastAPI                          |
| Межсервисная связь    | gRPC (grpcio, grpcio-tools)      |
| ORM                   | SQLAlchemy 2.0+ (async)          |
| Миграции              | Alembic                          |
| База данных           | PostgreSQL 15+                   |
| Хранение файлов       | MinIO (S3-совместимое хранилище) |
| Кэш / Брокер          | Redis                            |
| Контейнеризация       | Docker, Docker Compose           |
| Документация API      | Swagger UI (встроенный FastAPI)  |
| Линтер / Форматтер    | Ruff                             |
| Типизация             | mypy (strict mode)               |
| Менеджер зависимостей | Poetry                           |
| Тестирование          | pytest, pytest-asyncio, httpx    |
| Логирование           | structlog + Loki                 |
| Метрики               | Prometheus + Grafana             |

### 1.3 Перечень микросервисов

| №   | Сервис              | Порт REST | Порт gRPC | Префикс API            |
| --- | ------------------- | --------- | --------- | ---------------------- |
| 1   | auth-service        | 8001      | 50051     | `/api/v1/auth`         |
| 2   | patrol-service      | 8002      | 50052     | `/api/v1/patrols`      |
| 3   | duty-service        | 8003      | 50053     | `/api/v1/duties`       |
| 4   | coworking-service   | 8004      | 50054     | `/api/v1/coworkings`   |
| 5   | application-service | 8005      | 50055     | `/api/v1/applications` |

---

## 2. Архитектура проекта

### 2.1 Общая схема

```
                        ┌──────────────┐
                        │   API Gateway│  (Nginx / Traefik)
                        │   / Frontend │
                        └──────┬───────┘
                               │  REST (HTTP/JSON)
          ┌────────────┬───────┼───────┬────────────┐
          ▼            ▼       ▼       ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  auth    │ │ patrol   │ │  duty    │ │coworking │ │applicat. │
    │ service  │ │ service  │ │ service  │ │ service  │ │ service  │
    └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
         │            │            │            │            │
         │  gRPC      │  gRPC      │            │            │  gRPC
         │◄───────────┘            │            │            │◄─── (patrol)
         │◄────────────────────────┘            │            │
         │◄─────────────────────────────────────┘            │
         │                                                   │
    ┌────▼─────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
    │ auth_db  │  │patrol_db │  │ duty_db  │  │cowrk_db  │  │
    └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
                                                       ┌────▼─────┐
                                                       │ apps_db  │
                                                       └──────────┘
```

### 2.2 Принципы взаимодействия

- **Клиент → Сервис**: REST API (JSON over HTTP/HTTPS).
- **Сервис → Сервис**: gRPC (Protobuf). Используется для:
  - Валидации JWT-токенов через auth-service.
  - Получения данных о пользователях (ФИО, комната, подъезд) из auth-service.
  - Передачи данных заявлений в patrol-service из application-service.
- Каждый микросервис имеет **собственную базу данных** (Database per Service).
- Межсервисные данные **не дублируются** — при необходимости запрашиваются через gRPC.
- **Трассировка**: все запросы содержат `X-Trace-ID` и `X-Correlation-ID` для распределённой трассировки.

---

## 3. Структура микросервиса

> **См. детальную структуру в [PYTHON-GUIDELINES.md](./PYTHON-GUIDELINES.md#модульная-структура)**

Краткая структура:

```
service-name/
├── alembic/                    # Миграции БД
├── src/
│   ├── main.py                 # Точка входа FastAPI
│   ├── config.py               # Pydantic Settings
│   ├── api/v1/                 # REST API endpoints
│   ├── services/               # Бизнес-логика
│   ├── repositories/           # Data Access Layer
│   ├── models/                 # SQLAlchemy модели
│   ├── grpc_server/            # gRPC сервер
│   └── grpc_clients/           # gRPC клиенты
├── proto/                      # .proto контракты
├── tests/                      # Тесты
├── Dockerfile
└── pyproject.toml
```

---

## 4. API-контракты (REST)

### 4.1 Формат URL

```
{protocol}://{host}:{port}/api/v{version}/{resource}
```

Пример: `https://campus.sirius.ru/api/v1/duties/schedules`

### 4.2 HTTP-методы

| Метод    | Назначение                   | Идемпотентный |
| -------- | ---------------------------- | ------------- |
| `GET`    | Получение ресурса / списка   | Да            |
| `POST`   | Создание ресурса             | Нет           |
| `PUT`    | Полное обновление ресурса    | Да            |
| `PATCH`  | Частичное обновление ресурса | Да            |
| `DELETE` | Удаление ресурса             | Да            |

### 4.3 HTTP-статусы ответов

| Код | Использование                                     |
| --- | ------------------------------------------------- |
| 200 | Успешный запрос (GET, PUT, PATCH)                 |
| 201 | Ресурс создан (POST)                              |
| 204 | Успешно, без тела ответа (DELETE)                 |
| 400 | Ошибка валидации / некорректный запрос            |
| 401 | Не аутентифицирован                               |
| 403 | Нет прав доступа                                  |
| 404 | Ресурс не найден                                  |
| 409 | Конфликт (дублирование данных)                    |
| 422 | Ошибка валидации Pydantic (автоматически FastAPI) |
| 500 | Внутренняя ошибка сервера                         |

### 4.4 Формат успешного ответа (единичный ресурс)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "room_number": "304",
  "duty_date": "2025-12-01",
  "status": "pending",
  "created_at": "2025-11-25T10:30:00Z",
  "updated_at": "2025-11-25T10:30:00Z"
}
```

### 4.5 Формат успешного ответа (список с пагинацией)

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "room_number": "304",
      "duty_date": "2025-12-01"
    }
  ],
  "total": 48,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

### 4.6 Параметры пагинации (query)

| Параметр | Тип | По умолчанию | Описание                |
| -------- | --- | ------------ | ----------------------- |
| `page`   | int | 1            | Номер страницы (от 1)   |
| `size`   | int | 20           | Кол-во элементов (≤100) |

### 4.7 Формат ответа об ошибке

Все ошибки возвращаются в **единообразном формате** с обязательным `trace_id`:

```json
{
  "error": {
    "code": "DUTY_NOT_FOUND",
    "message": "Дежурство с указанным ID не найдено.",
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "details": null
  }
}
```

### 4.8 Единые коды ошибок

Каждый сервис определяет свои коды ошибок с **общим префиксом**:

| Сервис      | Префикс   | Пример кода ошибки        |
| ----------- | --------- | ------------------------- |
| auth        | `AUTH_`   | `AUTH_INVALID_TOKEN`      |
| patrol      | `PATROL_` | `PATROL_NOT_COMPLETED`    |
| duty        | `DUTY_`   | `DUTY_ALREADY_ASSIGNED`   |
| coworking   | `COWRK_`  | `COWRK_KEY_NOT_AVAILABLE` |
| application | `APP_`    | `APP_DOCUMENT_NOT_FOUND`  |

Общие коды (используются всеми сервисами):

| Код                | HTTP-статус | Описание                        |
| ------------------ | ----------- | ------------------------------- |
| `VALIDATION_ERROR` | 400 / 422   | Ошибка валидации входных данных |
| `UNAUTHORIZED`     | 401         | Токен отсутствует или невалиден |
| `FORBIDDEN`        | 403         | Недостаточно прав               |
| `NOT_FOUND`        | 404         | Ресурс не найден                |
| `CONFLICT`         | 409         | Конфликт данных                 |
| `INTERNAL_ERROR`   | 500         | Внутренняя ошибка               |

### 4.9 Формат даты и времени

- **Хранение в БД**: `TIMESTAMP WITH TIME ZONE`, временная зона — **UTC**.
- **Передача в API** (JSON): формат **ISO 8601** (`2025-12-01T10:30:00Z`, дата без времени — `2025-12-01`).
- **Отображение на клиенте**: формат, принятый в России — **дд.мм.гггг** (`01.12.2025`), время — **чч:мм** (`10:30`), дата и время — **дд.мм.гггг чч:мм** (`01.12.2025 10:30`).
- Конвертация из ISO 8601 в отображаемый формат выполняется **на стороне клиента (фронтенда)**.

### 4.10 Идентификаторы

- Первичные ключи — **UUID v4**.
- Передаются в URL и JSON как **строки**: `"550e8400-e29b-41d4-a716-446655440000"`.

### 4.11 Версионирование API

- Версия указывается в URL: `/api/v1/...`
- При мажорных изменениях создаётся `/api/v2/...`, предыдущая версия поддерживается минимум 1 мажорный релиз.

### 4.12 Обязательные HTTP-заголовки

**Request:**

- `Authorization: Bearer <token>` — JWT access token
- `X-Trace-ID` — (опционально) для продолжения трассировки
- `X-Correlation-ID` — (опционально) для группировки операций

**Response:**

- `X-Trace-ID` — всегда присутствует
- `X-Correlation-ID` — всегда присутствует

---

## 5. gRPC-контракты (межсервисное взаимодействие)

### 5.1 Общие правила proto-файлов

- Версия синтаксиса: `proto3`.
- Один `.proto` файл на сервис-провайдер.
- Пакет: `campus.<service_name>`.
- Все `.proto` файлы хранятся в **общем репозитории** `proto/` или дублируются в каждом сервисе.
- Сообщения именуются в `PascalCase`, поля — в `snake_case`.

### 5.2 Proto-контракт auth-service

```protobuf
syntax = "proto3";

package campus.auth;

service AuthService {
  // Валидация JWT-токена и получение данных пользователя
  rpc ValidateToken(ValidateTokenRequest) returns (ValidateTokenResponse);

  // Получение информации о пользователе по ID
  rpc GetUserInfo(GetUserInfoRequest) returns (UserInfoResponse);

  // Получение списка пользователей по фильтрам (комната, подъезд, корпус)
  rpc GetUsers(GetUsersRequest) returns (GetUsersResponse);

  // Проверка роли пользователя
  rpc CheckUserRole(CheckUserRoleRequest) returns (CheckUserRoleResponse);
}

message ValidateTokenRequest {
  string token = 1;
}

message ValidateTokenResponse {
  bool valid = 1;
  string user_id = 2;          // UUID
  repeated string roles = 3;   // ["student"], ["student", "student_head"], etc.
  string building = 4;         // "8" | "9"
  int32 entrance = 5;          // 1..4
  int32 floor = 6;             // 1..5
  string room = 7;             // "301"
}

message GetUserInfoRequest {
  string user_id = 1;
}

message UserInfoResponse {
  string user_id = 1;
  string last_name = 2;
  string first_name = 3;
  string patronymic = 4;
  string building = 5;
  int32 entrance = 6;
  int32 floor = 7;
  string room = 8;
  repeated string roles = 9;   // ["student"], ["educator", "educator_head"], etc.
  string phone = 10;
  string email = 11;
  bool is_minor = 12;          // несовершеннолетний
}

message GetUsersRequest {
  string building = 1;         // опционально
  int32 entrance = 2;          // опционально, 0 = все
  int32 floor = 3;             // опционально, 0 = все
  string room = 4;             // опционально
  string role = 5;             // опционально, фильтр по одной из ролей пользователя
  int32 page = 6;              // номер страницы (от 1), 0 = все
  int32 size = 7;              // кол-во на странице (≤100), 0 = все
}

message GetUsersResponse {
  repeated UserInfoResponse users = 1;
  int32 total = 2;             // общее кол-во по фильтру
  int32 page = 3;              // текущая страница
  int32 size = 4;              // размер страницы
  int32 pages = 5;             // общее кол-во страниц
}

message CheckUserRoleRequest {
  string user_id = 1;
  string required_role = 2;
}

message CheckUserRoleResponse {
  bool has_role = 1;
}
```

### 5.3 Proto-контракт application-service (для patrol-service)

```protobuf
syntax = "proto3";

package campus.application;

service ApplicationService {
  // Получение одобренных заявлений на выход для конкретной даты
  rpc GetApprovedLeaves(GetApprovedLeavesRequest) returns (GetApprovedLeavesResponse);
}

message GetApprovedLeavesRequest {
  string date = 1;             // ISO 8601 дата (YYYY-MM-DD)
  string building = 2;
  int32 entrance = 3;          // 0 = все
}

message GetApprovedLeavesResponse {
  repeated LeaveRecord records = 1;
}

message LeaveRecord {
  string user_id = 1;
  string user_name = 2;
  string room = 3;
  string leave_time = 4;       // ISO 8601
  string return_time = 5;      // ISO 8601
  string reason = 6;
}
```

### 5.4 Правила gRPC-взаимодействия

1. **Таймауты**: каждый gRPC-вызов имеет таймаут **5 секунд** по умолчанию.
2. **Ретраи**: при `UNAVAILABLE` — до 3 попыток с экспоненциальным бэкоффом.
3. **Трассировка**: передача `x-trace-id` и `x-correlation-id` через metadata (см. PYTHON-GUIDELINES.md).
4. **Обработка ошибок**: gRPC-статусы маппятся на HTTP-статусы:

| gRPC-статус         | HTTP-статус |
| ------------------- | ----------- |
| `OK`                | 200         |
| `INVALID_ARGUMENT`  | 400         |
| `UNAUTHENTICATED`   | 401         |
| `PERMISSION_DENIED` | 403         |
| `NOT_FOUND`         | 404         |
| `ALREADY_EXISTS`    | 409         |
| `UNAVAILABLE`       | 503         |
| `INTERNAL`          | 500         |

---

## 6. Аутентификация и авторизация

### 6.1 JWT-токены

- Используются **два типа** токенов:
  - **Access Token** — короткоживущий (15 минут), передаётся в заголовке `Authorization: Bearer <token>`.
  - **Refresh Token** — долгоживущий (7 дней), передаётся в httpOnly cookie или в теле запроса.

### 6.2 Payload Access Token

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "roles": ["student"],
  "building": "8",
  "entrance": 2,
  "room": "304",
  "is_minor": false,
  "exp": 1700000000,
  "iat": 1699999100,
  "jti": "unique-token-id"
}
```

### 6.3 Роли в системе

| Код роли         | Числовой уровень | Описание                                    |
| ---------------- | ---------------- | ------------------------------------------- |
| `student`        | 1.0              | Обычный студент                             |
| `student_patrol` | 1.1              | Студент-обходной                            |
| `student_head`   | 1.2              | Староста подъезда                           |
| `educator`       | 2.0              | Воспитатель                                 |
| `educator_head`  | 2.1              | Воспитатель, ответственный за подъезд       |
| `admin`          | 2.2              | Дежурный администратор (ночной воспитатель) |

- Один пользователь может иметь **несколько ролей** (хранятся как массив `roles` в JWT payload и в таблице `user_roles` в БД).

---

## 7. Docker и деплой

### 7.1 Dockerfile (эталон)

```dockerfile
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Установка зависимостей
FROM base AS deps
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only main

# Финальный образ
FROM base AS runtime
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY . .

EXPOSE 8001 50051

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 7.2 Docker Compose (dev-окружение)

```yaml
version: '3.9'

services:
  postgres-auth:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: campus
      POSTGRES_PASSWORD: campus_secret
      POSTGRES_DB: auth_db
    ports:
      - '5432:5432'
    volumes:
      - pg_auth_data:/var/lib/postgresql/data

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

  postgres-duty:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: campus
      POSTGRES_PASSWORD: campus_secret
      POSTGRES_DB: duty_db
    ports:
      - '5434:5432'
    volumes:
      - pg_duty_data:/var/lib/postgresql/data

  postgres-coworking:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: campus
      POSTGRES_PASSWORD: campus_secret
      POSTGRES_DB: coworking_db
    ports:
      - '5435:5432'
    volumes:
      - pg_coworking_data:/var/lib/postgresql/data

  postgres-application:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: campus
      POSTGRES_PASSWORD: campus_secret
      POSTGRES_DB: application_db
    ports:
      - '5436:5432'
    volumes:
      - pg_application_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - '9000:9000'
      - '9001:9001'
    volumes:
      - minio_data:/data

  loki:
    image: grafana/loki:2.9.0
    ports:
      - '3100:3100'
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - loki_data:/loki

  prometheus:
    image: prom/prometheus:latest
    ports:
      - '9090:9090'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - '3000:3000'
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - loki
      - prometheus

  auth-service:
    build: ./auth-service
    ports:
      - '8001:8001'
      - '50051:50051'
    env_file: ./auth-service/.env
    environment:
      - LOKI_URL=http://loki:3100
      - DATABASE_URL=postgresql+asyncpg://campus:campus_secret@postgres-auth:5432/auth_db
    depends_on:
      - postgres-auth
      - redis
      - loki

  # Аналогично для остальных сервисов:
  # patrol-service   → postgres-patrol   (patrol_db,   порт 5433)
  # duty-service     → postgres-duty     (duty_db,     порт 5434)
  # coworking-service→ postgres-coworking(coworking_db, порт 5435)
  # application-service→ postgres-application(application_db, порт 5436)

volumes:
  pg_auth_data:
  pg_patrol_data:
  pg_duty_data:
  pg_coworking_data:
  pg_application_data:
  minio_data:
  loki_data:
  prometheus_data:
  grafana_data:
```

---

## 8. Версионирование и Git

### 8.1 Структура репозитория

```
campus-sirius/
├── proto/                      # Общие .proto файлы
├── auth-service/
├── patrol-service/
├── duty-service/
├── coworking-service/
├── application-service/
├── frontend/                   # Vue.js приложение
├── docker-compose.yml
├── prometheus.yml
├── .gitignore
├── PYTHON-GUIDELINES.md        # Детальные требования к коду
├── FRONTEND-GUIDELINES.md      # Требования к фронтенду
├── tz-0-api-contracts-and-code-standards.md  # API-контракты
└── README.md
```

### 8.2 Git-конвенции

**Формат коммитов** (Conventional Commits):

```
<type>(<scope>): <описание>
```

| Тип        | Назначение                       |
| ---------- | -------------------------------- |
| `feat`     | Новая функциональность           |
| `fix`      | Исправление бага                 |
| `refactor` | Рефакторинг без изменения логики |
| `docs`     | Документация                     |
| `test`     | Тесты                            |
| `chore`    | Настройка инфраструктуры         |

**Scope** = название микросервиса (`auth`, `patrol`, `duty`, `coworking`, `app`, `frontend`) или `proto`, `docker`, `ci`.

### 8.3 Ветвление

| Ветка               | Назначение                          |
| ------------------- | ----------------------------------- |
| `main`              | Стабильная версия, готовая к деплою |
| `develop`           | Интеграционная ветка                |
| `feature/<name>`    | Разработка фичи                     |
| `fix/<name>`        | Исправление бага                    |
| `release/<version>` | Подготовка релиза                   |

---

> **Данный документ описывает API-контракты проекта «Кампус Сириус». Детальные требования к реализации см. в соответствующих GUIDELINES.**
