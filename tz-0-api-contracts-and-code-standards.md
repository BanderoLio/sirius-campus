# ТЗ-0: API-контракты и единые правила написания кода

## Содержание

1. [Общие сведения](#1-общие-сведения)
2. [Архитектура проекта](#2-архитектура-проекта)
3. [Структура микросервиса](#3-структура-микросервиса)
4. [Стандарты написания кода](#4-стандарты-написания-кода)
5. [API-контракты (REST)](#5-api-контракты-rest)
6. [gRPC-контракты (межсервисное взаимодействие)](#6-grpc-контракты-межсервисное-взаимодействие)
7. [Аутентификация и авторизация](#7-аутентификация-и-авторизация)
8. [Работа с базой данных](#8-работа-с-базой-данных)
9. [Обработка ошибок](#9-обработка-ошибок)
10. [Логирование](#10-логирование)
11. [Конфигурация и переменные окружения](#11-конфигурация-и-переменные-окружения)
12. [Тестирование](#12-тестирование)
13. [Docker и деплой](#13-docker-и-деплой)
14. [Версионирование и Git](#14-версионирование-и-git)

---

## 1. Общие сведения

### 1.1 Название проекта

**Кампус Сириус** — веб-приложение для автоматизации работы воспитателей и улучшения пользовательского опыта студентов Колледжа Сириус.

### 1.2 Стек технологий

| Компонент            | Технология                          |
|----------------------|-------------------------------------|
| Язык                 | Python 3.11+                        |
| Web-фреймворк        | FastAPI                             |
| Межсервисная связь   | gRPC (grpcio, grpcio-tools)         |
| ORM                  | SQLAlchemy 2.0+ (async)             |
| Миграции             | Alembic                             |
| База данных          | PostgreSQL 15+                      |
| Хранение файлов      | MinIO (S3-совместимое хранилище)     |
| Кэш / Брокер         | Redis                               |
| Контейнеризация      | Docker, Docker Compose              |
| Документация API     | Swagger UI (встроенный FastAPI)      |
| Линтер / Форматтер   | Ruff                                |
| Типизация            | mypy (strict mode)                  |
| Менеджер зависимостей | Poetry                              |
| Тестирование         | pytest, pytest-asyncio, httpx       |

### 1.3 Перечень микросервисов

| №  | Сервис                    | Порт REST | Порт gRPC | Префикс API            |
|----|---------------------------|-----------|-----------|-------------------------|
| 1  | auth-service              | 8001      | 50051     | `/api/v1/auth`          |
| 2  | patrol-service            | 8002      | 50052     | `/api/v1/patrols`       |
| 3  | duty-service              | 8003      | 50053     | `/api/v1/duties`        |
| 4  | coworking-service         | 8004      | 50054     | `/api/v1/coworkings`    |
| 5  | application-service       | 8005      | 50055     | `/api/v1/applications`  |

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

---

## 3. Структура микросервиса

Каждый микросервис **обязан** следовать единой структуре каталогов:

```
service-name/
├── alembic/                    # Миграции БД
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── src/
│   ├── __init__.py
│   ├── main.py                 # Точка входа FastAPI
│   ├── config.py               # Настройки приложения (Pydantic Settings)
│   ├── dependencies.py         # FastAPI Dependencies (DI)
│   ├── exceptions.py           # Кастомные исключения
│   ├── constants.py            # Константы модуля
│   │
│   ├── api/                    # REST API слой
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Агрегирующий роутер v1
│   │       ├── <entity>/
│   │       │   ├── __init__.py
│   │       │   ├── router.py   # Эндпоинты сущности
│   │       │   ├── schemas.py  # Pydantic-схемы запросов/ответов
│   │       │   └── dependencies.py  # Зависимости эндпоинтов
│   │       └── ...
│   │
│   ├── services/               # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── <entity>_service.py
│   │   └── ...
│   │
│   ├── repositories/           # Слой доступа к данным (DAL)
│   │   ├── __init__.py
│   │   ├── base.py             # Базовый репозиторий
│   │   ├── <entity>_repo.py
│   │   └── ...
│   │
│   ├── models/                 # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── base.py             # DeclarativeBase, общие миксины
│   │   ├── <entity>.py
│   │   └── ...
│   │
│   ├── grpc_server/            # gRPC серверная часть (если сервис предоставляет gRPC)
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── servicers/
│   │       ├── __init__.py
│   │       └── <service>_servicer.py
│   │
│   ├── grpc_clients/           # gRPC клиенты для обращения к другим сервисам
│   │   ├── __init__.py
│   │   └── auth_client.py
│   │
│   └── utils/                  # Утилиты
│       ├── __init__.py
│       └── ...
│
├── proto/                      # .proto файлы (контракты gRPC)
│   └── <service_name>.proto
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_repositories/
│
├── Dockerfile
├── pyproject.toml
├── poetry.lock
└── README.md
```

### 3.1 Слоистая архитектура (обязательна)

```
Router (API) → Service (бизнес-логика) → Repository (доступ к данным) → Model (ORM)
```

- **Router** — принимает HTTP-запрос, валидирует входные данные через Pydantic-схемы, вызывает сервис, возвращает ответ.
- **Service** — содержит всю бизнес-логику. Не знает о HTTP (не импортирует `Request`, `Response`). Работает с репозиториями.
- **Repository** — абстрагирует работу с БД. CRUD-операции, запросы. Не содержит бизнес-логику.
- **Model** — SQLAlchemy-модель, отражение таблицы в БД.

---

## 4. Стандарты написания кода

### 4.1 Общие правила

| Правило                          | Стандарт                                         |
|----------------------------------|--------------------------------------------------|
| Версия Python                    | 3.11+                                            |
| Стиль кода                      | PEP 8                                            |
| Максимальная длина строки        | 99 символов                                      |
| Форматирование                   | Ruff formatter (`ruff format`)                   |
| Линтинг                         | Ruff linter (`ruff check`)                       |
| Типизация                       | Обязательна для всех публичных функций и методов |
| Docstrings                      | Google-стиль                                     |
| Язык кода (переменные, функции) | Английский                                       |
| Язык комментариев               | Русский (допускается английский)                 |

### 4.2 Именование

| Сущность               | Конвенция               | Пример                          |
|-------------------------|-------------------------|---------------------------------|
| Модули / файлы          | snake_case              | `duty_service.py`               |
| Классы                  | PascalCase              | `DutySchedule`                  |
| Функции / методы        | snake_case              | `get_duty_by_id()`              |
| Переменные              | snake_case              | `current_user`                  |
| Константы               | UPPER_SNAKE_CASE        | `MAX_COWORKING_HOURS`           |
| Pydantic-схемы          | PascalCase + суффикс    | `DutyCreateRequest`, `DutyResponse` |
| SQLAlchemy-модели       | PascalCase (ед. число)  | `User`, `DutySchedule`          |
| Таблицы в БД            | snake_case (мн. число)  | `users`, `duty_schedules`       |
| Эндпоинты               | kebab-case (мн. число)  | `/api/v1/duties/schedules`      |
| Proto-сервисы           | PascalCase              | `AuthService`                   |
| Proto-сообщения         | PascalCase              | `UserInfoRequest`               |
| Переменные окружения    | UPPER_SNAKE_CASE        | `DATABASE_URL`                  |

### 4.3 Импорты

Порядок импортов (управляется Ruff автоматически):

```python
# 1. Стандартная библиотека
import os
from datetime import datetime, timezone
from uuid import UUID

# 2. Сторонние библиотеки
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Локальные модули
from src.models.user import User
from src.services.user_service import UserService
```

### 4.4 Асинхронность

- Все эндпоинты **должны быть асинхронными** (`async def`).
- Все операции ввода-вывода (БД, HTTP, файлы) — **асинхронные**.
- Используемые библиотеки: `asyncpg`, `aiohttp` / `httpx`, `aiofiles`.
- SQLAlchemy: только через `AsyncSession` и `AsyncEngine`.

### 4.5 Пример эндпоинта (эталон)

```python
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.v1.duties.schemas import (
    DutyCreateRequest,
    DutyResponse,
)
from src.dependencies import get_current_user, get_duty_service
from src.models.user import User
from src.services.duty_service import DutyService

router = APIRouter(prefix="/duties", tags=["Дежурства"])


@router.post(
    "/",
    response_model=DutyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать дежурство",
    description="Создание записи о дежурстве для конкретной комнаты.",
)
async def create_duty(
    body: DutyCreateRequest,
    current_user: User = Depends(get_current_user),
    duty_service: DutyService = Depends(get_duty_service),
) -> DutyResponse:
    """Создать новое дежурство."""
    duty = await duty_service.create_duty(
        data=body,
        created_by=current_user.id,
    )
    return DutyResponse.model_validate(duty)
```

---

## 5. API-контракты (REST)

### 5.1 Формат URL

```
{protocol}://{host}:{port}/api/v{version}/{resource}
```

Пример: `https://campus.sirius.ru/api/v1/duties/schedules`

### 5.2 HTTP-методы

| Метод    | Назначение                     | Идемпотентный |
|----------|-------------------------------|---------------|
| `GET`    | Получение ресурса / списка    | Да            |
| `POST`   | Создание ресурса              | Нет           |
| `PUT`    | Полное обновление ресурса     | Да            |
| `PATCH`  | Частичное обновление ресурса  | Да            |
| `DELETE` | Удаление ресурса              | Да            |

### 5.3 HTTP-статусы ответов

| Код  | Использование                                        |
|------|------------------------------------------------------|
| 200  | Успешный запрос (GET, PUT, PATCH)                    |
| 201  | Ресурс создан (POST)                                |
| 204  | Успешно, без тела ответа (DELETE)                    |
| 400  | Ошибка валидации / некорректный запрос               |
| 401  | Не аутентифицирован                                  |
| 403  | Нет прав доступа                                     |
| 404  | Ресурс не найден                                     |
| 409  | Конфликт (дублирование данных)                       |
| 422  | Ошибка валидации Pydantic (автоматически FastAPI)    |
| 500  | Внутренняя ошибка сервера                            |

### 5.4 Формат успешного ответа (единичный ресурс)

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

### 5.5 Формат успешного ответа (список с пагинацией)

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

Pydantic-схема пагинации (единая для всех сервисов):

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Обёртка для пагинированных ответов."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int
```

### 5.6 Параметры пагинации (query)

| Параметр | Тип  | По умолчанию | Описание                |
|----------|------|--------------|-------------------------|
| `page`   | int  | 1            | Номер страницы (от 1)   |
| `size`   | int  | 20           | Кол-во элементов (≤100) |

### 5.7 Формат ответа об ошибке

Все ошибки возвращаются в **единообразном формате**:

```json
{
  "error": {
    "code": "DUTY_NOT_FOUND",
    "message": "Дежурство с указанным ID не найдено.",
    "details": null
  }
}
```

Pydantic-схема:

```python
from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Тело ошибки."""

    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    """Обёртка для ответа с ошибкой."""

    error: ErrorDetail
```

### 5.8 Единые коды ошибок

Каждый сервис определяет свои коды ошибок с **общим префиксом**:

| Сервис       | Префикс    | Пример кода ошибки        |
|-------------|------------|---------------------------|
| auth        | `AUTH_`    | `AUTH_INVALID_TOKEN`       |
| patrol      | `PATROL_`  | `PATROL_NOT_COMPLETED`     |
| duty        | `DUTY_`    | `DUTY_ALREADY_ASSIGNED`    |
| coworking   | `COWRK_`   | `COWRK_KEY_NOT_AVAILABLE`  |
| application | `APP_`     | `APP_DOCUMENT_NOT_FOUND`   |

Общие коды (используются всеми сервисами):

| Код                    | HTTP-статус | Описание                          |
|------------------------|-------------|-----------------------------------|
| `VALIDATION_ERROR`     | 400 / 422   | Ошибка валидации входных данных   |
| `UNAUTHORIZED`         | 401         | Токен отсутствует или невалиден   |
| `FORBIDDEN`            | 403         | Недостаточно прав                 |
| `NOT_FOUND`            | 404         | Ресурс не найден                  |
| `CONFLICT`             | 409         | Конфликт данных                   |
| `INTERNAL_ERROR`       | 500         | Внутренняя ошибка                 |

### 5.9 Формат даты и времени

- **Хранение в БД**: `TIMESTAMP WITH TIME ZONE`, временная зона — **UTC**.
- **Передача в API** (JSON): формат **ISO 8601** (`2025-12-01T10:30:00Z`, дата без времени — `2025-12-01`).
- **Отображение на клиенте**: формат, принятый в России — **дд.мм.гггг** (`01.12.2025`), время — **чч:мм** (`10:30`), дата и время — **дд.мм.гггг чч:мм** (`01.12.2025 10:30`).
- Конвертация из ISO 8601 в отображаемый формат выполняется **на стороне клиента (фронтенда)**.
- При необходимости серверной генерации отображаемых строк (уведомления, отчёты) использовать утилиту форматирования:

```python
from datetime import datetime


def format_date_ru(dt: datetime) -> str:
    """Форматировать дату в российский формат дд.мм.гггг."""
    return dt.strftime("%d.%m.%Y")


def format_datetime_ru(dt: datetime) -> str:
    """Форматировать дату и время в российский формат дд.мм.гггг чч:мм."""
    return dt.strftime("%d.%m.%Y %H:%M")
```

### 5.10 Идентификаторы

- Первичные ключи — **UUID v4**.
- Передаются в URL и JSON как **строки**: `"550e8400-e29b-41d4-a716-446655440000"`.

### 5.11 Версионирование API

- Версия указывается в URL: `/api/v1/...`
- При мажорных изменениях создаётся `/api/v2/...`, предыдущая версия поддерживается минимум 1 мажорный релиз.

---

## 6. gRPC-контракты (межсервисное взаимодействие)

### 6.1 Общие правила proto-файлов

- Версия синтаксиса: `proto3`.
- Один `.proto` файл на сервис-провайдер.
- Пакет: `campus.<service_name>`.
- Все `.proto` файлы хранятся в **общем репозитории** `proto/` или дублируются в каждом сервисе.
- Сообщения именуются в `PascalCase`, поля — в `snake_case`.

### 6.2 Proto-контракт auth-service

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
  string role = 3;             // "student" | "student_patrol" | "student_head" | "educator" | "educator_head" | "admin"
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
  string role = 9;
  string phone = 10;
  string email = 11;
  bool is_minor = 12;          // несовершеннолетний
}

message GetUsersRequest {
  string building = 1;         // опционально
  int32 entrance = 2;          // опционально, 0 = все
  int32 floor = 3;             // опционально, 0 = все
  string room = 4;             // опционально
  string role = 5;             // опционально
}

message GetUsersResponse {
  repeated UserInfoResponse users = 1;
}

message CheckUserRoleRequest {
  string user_id = 1;
  string required_role = 2;
}

message CheckUserRoleResponse {
  bool has_role = 1;
}
```

### 6.3 Proto-контракт application-service (для patrol-service)

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

### 6.4 Правила gRPC-взаимодействия

1. **Таймауты**: каждый gRPC-вызов имеет таймаут **5 секунд** по умолчанию.
2. **Ретраи**: при `UNAVAILABLE` — до 3 попыток с экспоненциальным бэкоффом.
3. **Обработка ошибок**: gRPC-статусы маппятся на HTTP-статусы:

| gRPC-статус        | HTTP-статус |
|--------------------|-------------|
| `OK`               | 200         |
| `INVALID_ARGUMENT` | 400         |
| `UNAUTHENTICATED`  | 401         |
| `PERMISSION_DENIED`| 403         |
| `NOT_FOUND`        | 404         |
| `ALREADY_EXISTS`   | 409         |
| `UNAVAILABLE`      | 503         |
| `INTERNAL`         | 500         |

---

## 7. Аутентификация и авторизация

### 7.1 JWT-токены

- Используются **два типа** токенов:
  - **Access Token** — короткоживущий (15 минут), передаётся в заголовке `Authorization: Bearer <token>`.
  - **Refresh Token** — долгоживущий (7 дней), передаётся в httpOnly cookie или в теле запроса.

### 7.2 Payload Access Token

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "role": "student",
  "building": "8",
  "entrance": 2,
  "room": "304",
  "is_minor": false,
  "exp": 1700000000,
  "iat": 1699999100,
  "jti": "unique-token-id"
}
```

### 7.3 Роли в системе

| Код роли            | Числовой уровень | Описание                                  |
|---------------------|------------------|-------------------------------------------|
| `student`           | 1.0              | Обычный студент                           |
| `student_patrol`    | 1.1              | Студент-обходной                          |
| `student_head`      | 1.2              | Староста подъезда                         |
| `educator`          | 2.0              | Воспитатель                               |
| `educator_head`     | 2.1              | Воспитатель, ответственный за подъезд     |
| `admin`             | 2.2              | Дежурный администратор (ночной воспитатель) |

- Один пользователь может иметь **несколько ролей** (хранятся как массив).
- При авторизации роль проверяется через `Depends(require_role("educator"))`.

### 7.4 Middleware / Dependency для проверки доступа

Каждый сервис использует единый `Depends(get_current_user)`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_client: AuthGrpcClient = Depends(get_auth_client),
) -> UserContext:
    """Получить текущего пользователя через gRPC-валидацию токена."""
    token = credentials.credentials
    result = await auth_client.validate_token(token)
    if not result.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истёкший токен.",
        )
    return UserContext(
        user_id=result.user_id,
        role=result.role,
        building=result.building,
        entrance=result.entrance,
        room=result.room,
    )


def require_role(*roles: str):
    """Фабрика зависимостей для проверки роли."""
    async def _check_role(
        current_user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции.",
            )
        return current_user
    return _check_role
```

---

## 8. Работа с базой данных

### 8.1 Общие правила

- Каждый сервис использует **свою БД** (schema isolation или отдельная БД).
- ORM: SQLAlchemy 2.0+ (Mapped, mapped_column) с **async-драйвером** `asyncpg`.
- Миграции: Alembic (async mode).
- Все модели наследуются от общего `Base` с обязательными полями.

### 8.2 Базовая модель (обязательна для всех сервисов)

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовая модель для всех сущностей."""
    pass


class TimestampMixin:
    """Миксин с полями created_at и updated_at."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Миксин с UUID первичным ключом."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
```

### 8.3 Правила именования в БД

| Сущность           | Правило                     | Пример                       |
|--------------------|-----------------------------|------------------------------|
| Таблицы            | snake_case, мн. число       | `duty_schedules`             |
| Столбцы            | snake_case                  | `duty_date`                  |
| Внешние ключи      | `fk_{таблица}_{столбец}`    | `fk_duties_user_id`          |
| Индексы            | `ix_{таблица}_{столбец(ы)}` | `ix_duties_duty_date`        |
| Уникальные констр. | `uq_{таблица}_{столбец(ы)}` | `uq_users_email`             |
| Первичные ключи    | `pk_{таблица}`              | `pk_users`                   |

### 8.4 Управление сессиями

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения сессии БД."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

## 9. Обработка ошибок

### 9.1 Кастомные исключения

Каждый сервис определяет базовое исключение и наследников:

```python
from dataclasses import dataclass


@dataclass
class ServiceError(Exception):
    """Базовое исключение сервиса."""

    code: str
    message: str
    status_code: int = 400


class NotFoundError(ServiceError):
    """Ресурс не найден."""

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} с ID {resource_id} не найден.",
            status_code=404,
        )


class ForbiddenError(ServiceError):
    """Доступ запрещён."""

    def __init__(self, message: str = "Недостаточно прав.") -> None:
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
        )


class ConflictError(ServiceError):
    """Конфликт данных."""

    def __init__(self, message: str) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
        )
```

### 9.2 Глобальный обработчик исключений

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions import ServiceError


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация глобальных обработчиков ошибок."""

    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": None,
                }
            },
        )
```

---

## 10. Логирование

### 10.1 Формат

- Формат логов: **JSON** (structlog).
- Обязательные поля в каждой записи:

```json
{
  "timestamp": "2025-12-01T10:30:00.123Z",
  "level": "info",
  "service": "duty-service",
  "request_id": "abc123",
  "user_id": "550e8400-...",
  "message": "Дежурство создано",
  "extra": {}
}
```

### 10.2 Уровни логирования

| Уровень   | Использование                                      |
|-----------|---------------------------------------------------|
| `DEBUG`   | Детали выполнения (только локально)                |
| `INFO`    | Успешные операции, ключевые события                |
| `WARNING` | Подозрительные ситуации, но не ошибки              |
| `ERROR`   | Ошибки, требующие внимания                         |
| `CRITICAL`| Критические сбои (недоступность БД, gRPC-сервиса) |

### 10.3 Middleware для request_id

Каждый запрос получает уникальный `X-Request-ID` (генерируется при отсутствии):

```python
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

---

## 11. Конфигурация и переменные окружения

### 11.1 Подход

- Конфигурация через **Pydantic Settings** с чтением из `.env` файла.
- Секреты не коммитятся в репозиторий (`.env` в `.gitignore`).
- Обязателен файл `.env.example` с описанием всех переменных.

### 11.2 Пример config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Приложение
    app_name: str = "duty-service"
    debug: bool = False

    # База данных
    database_url: str
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT (только для auth-service; остальные валидируют через gRPC)
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # gRPC
    grpc_auth_host: str = "localhost"
    grpc_auth_port: int = 50051

    # MinIO (для сервисов с файлами)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_bucket: str = "campus"


settings = Settings()  # type: ignore[call-arg]
```

### 11.3 Обязательные переменные для каждого сервиса

| Переменная          | Описание                              | Обязательная |
|---------------------|--------------------------------------|:------------:|
| `DATABASE_URL`      | URL подключения к PostgreSQL         | ✅           |
| `REDIS_URL`         | URL подключения к Redis              | ✅           |
| `GRPC_AUTH_HOST`    | Хост auth-service (gRPC)            | ✅           |
| `GRPC_AUTH_PORT`    | Порт auth-service (gRPC)            | ✅           |
| `DEBUG`             | Режим отладки                        | ❌           |

---

## 12. Тестирование

### 12.1 Требования

- Минимальное покрытие: **70%** для бизнес-логики (services/).
- Типы тестов:
  - **Unit-тесты**: сервисы, утилиты (мокирование репозиториев).
  - **Интеграционные тесты**: API-эндпоинты (тестовая БД, httpx AsyncClient).

### 12.2 Структура тестов

```
tests/
├── conftest.py               # Фикстуры: тестовая БД, клиент, моки
├── test_api/
│   └── test_duties.py        # Тесты эндпоинтов
├── test_services/
│   └── test_duty_service.py  # Тесты бизнес-логики
└── test_repositories/
    └── test_duty_repo.py     # Тесты работы с БД
```

### 12.3 Пример conftest.py

```python
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Асинхронный тестовый клиент."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
```

---

## 13. Docker и деплой

### 13.1 Dockerfile (эталон)

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

### 13.2 Docker Compose (dev-окружение)

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: campus
      POSTGRES_PASSWORD: campus_secret
      POSTGRES_DB: campus
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  auth-service:
    build: ./auth-service
    ports:
      - "8001:8001"
      - "50051:50051"
    env_file: ./auth-service/.env
    depends_on:
      - postgres
      - redis

  patrol-service:
    build: ./patrol-service
    ports:
      - "8002:8002"
      - "50052:50052"
    env_file: ./patrol-service/.env
    depends_on:
      - postgres
      - auth-service

  duty-service:
    build: ./duty-service
    ports:
      - "8003:8003"
      - "50053:50053"
    env_file: ./duty-service/.env
    depends_on:
      - postgres
      - auth-service

  coworking-service:
    build: ./coworking-service
    ports:
      - "8004:8004"
      - "50054:50054"
    env_file: ./coworking-service/.env
    depends_on:
      - postgres
      - redis
      - auth-service

  application-service:
    build: ./application-service
    ports:
      - "8005:8005"
      - "50055:50055"
    env_file: ./application-service/.env
    depends_on:
      - postgres
      - minio
      - auth-service

volumes:
  pg_data:
  minio_data:
```

---

## 14. Версионирование и Git

### 14.1 Структура репозитория

```
campus-sirius/
├── proto/                      # Общие .proto файлы
├── auth-service/
├── patrol-service/
├── duty-service/
├── coworking-service/
├── application-service/
├── docker-compose.yml
├── .gitignore
└── README.md
```

### 14.2 Git-конвенции

**Формат коммитов** (Conventional Commits):

```
<type>(<scope>): <описание>
```

| Тип        | Назначение                         |
|------------|-----------------------------------|
| `feat`     | Новая функциональность            |
| `fix`      | Исправление бага                  |
| `refactor` | Рефакторинг без изменения логики  |
| `docs`     | Документация                      |
| `test`     | Тесты                            |
| `chore`    | Настройка инфраструктуры          |

Примеры:

```
feat(duty): добавить эндпоинт создания дежурства
fix(auth): исправить валидацию refresh-токена
refactor(coworking): вынести логику бронирования в сервис
docs(proto): обновить контракт AuthService
test(patrol): добавить тесты обхода комнат
chore(docker): обновить базовый образ Python
```

**Scope** = название микросервиса (`auth`, `patrol`, `duty`, `coworking`, `app`) или `proto`, `docker`, `ci`.

### 14.3 Ветвление

| Ветка              | Назначение                            |
|--------------------|--------------------------------------|
| `main`             | Стабильная версия, готовая к деплою  |
| `develop`          | Интеграционная ветка                 |
| `feature/<name>`   | Разработка фичи                      |
| `fix/<name>`       | Исправление бага                     |
| `release/<version>`| Подготовка релиза                    |

### 14.4 .gitignore (обязательные правила)

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/

# Окружение
.env
.env.local

# IDE
.idea/
.vscode/
*.swp

# Тесты
.coverage
htmlcov/
.pytest_cache/

# Docker
docker-compose.override.yml
```

---

> **Данный документ является обязательным к соблюдению всеми разработчиками проекта «Кампус Сириус». Любые отклонения от стандартов согласуются с командой через pull request и обсуждение.**

