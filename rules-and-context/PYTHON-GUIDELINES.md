# Python FastAPI Development Guidelines

Данный документ описывает правила разработки, best practices и архитектурные ограничения для проекта «Кампус Сириус» на Python FastAPI.

## Содержание

- [Архитектурные ограничения](#архитектурные-ограничения)
- [Обработка ошибок](#обработка-ошибок)
- [Управление конфигурацией](#управление-конфигурацией)
- [Стиль кода](#стиль-кода)
- [Тестирование](#тестирование)
- [Соглашения об именовании](#соглашения-об-именовании)

## Архитектурные ограничения

### Правила Domain-слоя

- **Без зависимостей от фреймворка**: Domain-слой не должен импортировать FastAPI, gRPC или любой транспортный код
- **Без кодов ошибок**: Domain-исключения содержат только сообщения, не коды ошибок
- **Чистая бизнес-логика**: Domain содержит только бизнес-правила и сущности
- **Без gRPC-исключений**: Используйте кастомные domain-исключения, не gRPC-статусы

### Правила Application-слоя (Services)

- **Без прямого доступа к БД**: Application-сервисы используют репозитории, никогда не обращаются к БД напрямую
- **Только Domain-исключения**: Выбрасывайте domain-исключения, не HTTP/gRPC-специфичные исключения
- **Без бизнес-логики в репозиториях**: Репозитории только для доступа к данным

### Правила Infrastructure-слоя

- **Маппинг исключений**: Преобразует domain-исключения в транспортные (HTTPException, gRPC-статусы)
- **Присваивание кодов ошибок**: Exception Handler присваивает коды ошибок из типизированных констант
- **Adapter Pattern**: Реализует domain-интерфейсы с фреймворк-специфичным кодом

### Правила Presentation-слоя (Routers)

- **Без бизнес-логики**: Роутеры только обрабатывают преобразование request/response
- **Без доступа к БД**: Роутеры никогда не обращаются к БД напрямую
- **Использование Application-сервисов**: Все бизнес-операции через application-сервисы

### Правила Repository

- **Без бизнес-логики**: Репозитории только обрабатывают доступ к данным
- **CRUD-операции**: Репозитории предоставляют базовый CRUD, без сложных бизнес-правил

### Application Service (Фасад / Public API)

- Если `Модуль A` нуждается в данных или действиях из `Модуля B`, он должен вызвать экспортированный Application Service из `Модуля B`
- **Реализация**: В FastAPI используйте зависимости через `Depends()` для инъекции сервисов
- **Преимущество**: Сервис действует как "привратник", обеспечивая применение всей бизнес-логики и валидаций

## Обработка ошибок

### Domain-исключения

Domain-исключения содержат только сообщения, без кодов ошибок:

```python
class AuthException(Exception):
    """Базовое исключение для auth-домена."""
    
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


class UserNotFoundException(AuthException):
    """Пользователь не найден."""
    
    def __init__(self, user_id: str | None = None, cause: Exception | None = None) -> None:
        message = f"User with id {user_id} not found" if user_id else "User not found"
        super().__init__(message, cause)
```

### Константы кодов ошибок

Коды ошибок определяются как константы в отдельном модуле. Эти константы могут быть переиспользованы во фронтенде для интернационализации:

```python
# src/constants/error_codes.py
from typing import Literal

# Auth Service Error Codes
AUTH_USER_NOT_FOUND: Literal["AUTH_USER_NOT_FOUND"] = "AUTH_USER_NOT_FOUND"
AUTH_USER_ALREADY_EXISTS: Literal["AUTH_USER_ALREADY_EXISTS"] = "AUTH_USER_ALREADY_EXISTS"
AUTH_INVALID_CREDENTIALS: Literal["AUTH_INVALID_CREDENTIALS"] = "AUTH_INVALID_CREDENTIALS"
AUTH_INVALID_TOKEN: Literal["AUTH_INVALID_TOKEN"] = "AUTH_INVALID_TOKEN"

# Type для всех auth-ошибок
AuthErrorCode = Literal[
    "AUTH_USER_NOT_FOUND",
    "AUTH_USER_ALREADY_EXISTS",
    "AUTH_INVALID_CREDENTIALS",
    "AUTH_INVALID_TOKEN",
]
```

**Важно**: Domain-исключения НЕ содержат коды ошибок. Коды присваиваются в Exception Handler'ах, используя эти константы.

### Маппинг исключений в Exception Handler

Exception Handler преобразует domain-исключения в коды ошибок:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions import AuthException, UserNotFoundException
from src.constants.error_codes import AUTH_USER_NOT_FOUND


async def auth_exception_handler(request: Request, exc: AuthException) -> JSONResponse:
    """Обработчик для auth-исключений."""
    error_code = _map_exception_to_code(exc)
    
    return JSONResponse(
        status_code=_get_status_code(exc),
        content={
            "error": {
                "code": error_code,
                "message": str(exc),
                "details": None,
            }
        },
    )


def _map_exception_to_code(exception: AuthException) -> str:
    """Преобразовать domain-исключение в код ошибки."""
    if isinstance(exception, UserNotFoundException):
        return AUTH_USER_NOT_FOUND
    # ...другие маппинги
    return "AUTH_UNKNOWN_ERROR"
```

### Формат ответа об ошибке

Все ошибки возвращаются в единообразном формате:

```json
{
  "error": {
    "code": "AUTH_USER_NOT_FOUND",
    "message": "User with id 123 not found",
    "details": null
  }
}
```

### Pydantic-схемы для ошибок

```python
from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Детали ошибки."""
    
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    """Обёртка для ответа с ошибкой."""
    
    error: ErrorDetail
```

## Управление конфигурацией

### Pydantic Settings

Вся конфигурация должна идти через `pydantic-settings`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    """JWT-конфигурация."""
    
    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        env_file=".env",
        case_sensitive=False,
    )
    
    secret: str = "change-me-in-production"
    access_exp_in: str = "15m"
    refresh_exp_in: str = "7d"
    algorithm: str = "HS256"


jwt_settings = JWTSettings()  # type: ignore[call-arg]
```

### Без прямого использования process.env

Никогда не используйте переменные окружения напрямую в коде приложения:

```python
# ❌ Плохо
import os
secret = os.getenv("JWT_SECRET")

# ✅ Хорошо
from src.config import jwt_settings
secret = jwt_settings.secret
```

### Без магических строк

Все строковые значения должны быть конфигурируемыми или константами:

```python
# ❌ Плохо
if payload.type != "ACCESS":
    pass

# ✅ Хорошо
from src.constants import TOKEN_TYPE_ACCESS

if payload.type != TOKEN_TYPE_ACCESS:
    pass
```

### Расположение конфигурационных файлов

Все конфигурационные файлы в директории `src/config/`:

- `jwt.py` - настройки JWT
- `auth.py` - настройки аутентификации
- `database.py` - настройки БД
- `app.py` - настройки приложения

## Стиль кода

### Без комментариев

Код должен быть самодокументируемым:

```python
# ❌ Плохо
# Validate user credentials
is_valid = await validate_credentials(user, password)

# ✅ Хорошо
is_valid = await validate_credentials(user, password)
```

Исключения:
- Сложные описания интерфейсов
- Документация публичного API (docstrings)

### Строгая типизация

- Включён strict mode в mypy
- Без типов `Any` (используйте `Unknown` когда необходимо)
- Предпочитайте Pydantic-модели для форм объектов
- Используйте type guards для runtime-валидации

### Type Hints

```python
from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(Protocol):
    """Интерфейс репозитория пользователей."""
    
    async def get_by_id(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:
        """Получить пользователя по ID."""
        ...
```

## Тестирование

### Unit-тесты

- **Фреймворк**: pytest для unit/integration тестирования
- **Расположение**: Тесты в директории `tests/` в корне проекта
- **Именование**: `test_*.py` для тестовых файлов
- **Покрытие**: Domain-логика должна иметь unit-тесты

### Структура тестов

```python
import pytest


class TestDutyService:
    """Тесты для DutyService."""
    
    async def test_create_duty_success(self) -> None:
        """Должен успешно создать дежурство."""
        # Arrange
        duty_data = DutyCreateRequest(...)
        
        # Act
        duty = await duty_service.create_duty(duty_data)
        
        # Assert
        assert duty.id is not None
        assert duty.status == "pending"
```

### Запуск тестов

```bash
cd auth-service
pytest
pytest --cov=src tests/  # с покрытием
```

## Соглашения об именовании

### Файлы

- **snake_case**: `auth_service.py`, `user_repository.py`

### Классы

- **PascalCase**: `AuthService`, `UserRepository`

### Функции и методы

- **snake_case**: `get_user_by_id`, `is_valid_token`

### Переменные

- **snake_case**: `current_user`, `access_token`

### Константы

- **UPPER_SNAKE_CASE**: `MAX_RETRY_COUNT`, `TOKEN_TYPE_ACCESS`

```python
# src/constants.py
from typing import Final

MAX_LOGIN_ATTEMPTS: Final[int] = 5
TOKEN_TYPE_ACCESS: Final[str] = "ACCESS"
TOKEN_TYPE_REFRESH: Final[str] = "REFRESH"
```

### Коды ошибок

- **UPPER_SNAKE_CASE** с префиксом сервиса: `AUTH_USER_NOT_FOUND`, `DUTY_ALREADY_ASSIGNED`

## Модульная структура

### Структура Feature

Каждая фича следует Clean Architecture:

```
feature/
├── domain/           # Entities, interfaces
├── services/         # Use cases, бизнес-логика
├── repositories/     # Адаптеры доступа к данным
└── routers/          # API endpoints, DTOs (schemas)
```

### Разделение модулей

- Каждый сервис имеет свои собственные entities и бизнес-логику
- Фичи — независимые модули
- Общий код в `common` или `core` папках

## Общие коды ошибок

Константы кодов ошибок в `src/constants/error_codes.py` могут быть переиспользованы во фронтенде:

- Обеспечивает интернационализацию
- Type-safe обработка ошибок
- Единообразные коды ошибок между сервисами

Пример использования во фронтенде:

```typescript
import { AUTH_USER_NOT_FOUND } from '@/constants/errorCodes';

if (error.code === AUTH_USER_NOT_FOUND) {
  // Обработать ошибку "пользователь не найден"
}
```

## Асинхронность

### Обязательные требования

- Все endpoint'ы должны быть асинхронными (`async def`)
- Все операции ввода-вывода (БД, HTTP, файлы) — асинхронные
- SQLAlchemy: только через `AsyncSession` и `AsyncEngine`
- HTTP-клиенты: `httpx.AsyncClient`
- Файловые операции: `aiofiles`

### Пример асинхронного endpoint'а

```python
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.v1.duties.schemas import DutyCreateRequest, DutyResponse
from src.dependencies import get_current_user, get_duty_service
from src.models.user import User
from src.services.duty_service import DutyService

router = APIRouter(prefix="/duties", tags=["Дежурства"])


@router.post(
    "/",
    response_model=DutyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать дежурство",
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

## Dependency Injection

### FastAPI Dependencies

Используйте `Depends()` для внедрения зависимостей:

```python
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """Получить репозиторий пользователей."""
    return UserRepository(session)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Получить сервис пользователей."""
    return UserService(repository)
```

## Логирование

### Структурированное логирование (Structlog)

Используйте structlog для структурированного JSON-логирования с обязательными полями:

```python
import structlog
from uuid import uuid4

logger = structlog.get_logger(__name__)

# Конфигурация structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### Обязательные поля в логах

Каждая запись лога должна содержать:

```json
{
  "timestamp": "2025-12-01T10:30:00.123Z",
  "level": "info",
  "service": "duty-service",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "correlation_id": "abc123-def456",
  "user_id": "550e8400-...",
  "request_method": "POST",
  "request_path": "/api/v1/duties",
  "message": "Дежурство создано",
  "duration_ms": 45.2
}
```

**Обязательные поля:**
```
| Поле              | Тип    | Описание                                           |
|-------------------|--------|----------------------------------------------------|
| `timestamp`       | string | ISO 8601 UTC timestamp                             |
| `level`           | string | Уровень логирования (debug, info, warning, error)  |
| `service`         | string | Название микросервиса                              |
| `trace_id`        | string | Уникальный ID для трассировки запроса по сервисам  |
| `correlation_id`  | string | ID для группировки связанных операций              |
| `message`         | string | Текстовое описание события                         |
```

**Опциональные поля:**
```
- `user_id` - UUID пользователя (если аутентифицирован)
- `request_method` - HTTP метод
- `request_path` - URL путь
- `duration_ms` - Длительность операции в миллисекундах
- `error` - Описание ошибки (при level=error)
- `stack_trace` - Stack trace (при исключениях)
```

### Middleware для Trace ID и Correlation ID

Каждый сервис должен использовать middleware для генерации/пропагации trace_id и correlation_id:

```python
import uuid
from contextvars import ContextVar

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware для управления trace_id и correlation_id."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Получить или сгенерировать trace_id
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        trace_id_var.set(trace_id)

        # Получить или сгенерировать correlation_id
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        correlation_id_var.set(correlation_id)

        # Добавить в structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            trace_id=trace_id,
            correlation_id=correlation_id,
            service=settings.app_name,
        )

        # Обработать запрос
        response = await call_next(request)

        # Добавить заголовки в ответ
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Correlation-ID"] = correlation_id

        return response


# Регистрация в main.py
app.add_middleware(TracingMiddleware)
```

### Логирование в сервисах

```python
import structlog
from contextvars import ContextVar

logger = structlog.get_logger(__name__)


async def create_duty(data: DutyCreateRequest, user_id: str) -> Duty:
    """Создать дежурство."""
    logger.info(
        "creating_duty",
        user_id=user_id,
        building=data.building,
        room=data.room,
        duty_date=str(data.duty_date),
    )

    try:
        duty = await duty_repository.create(data)
        logger.info(
            "duty_created",
            duty_id=str(duty.id),
            user_id=user_id,
        )
        return duty
    except Exception as e:
        logger.error(
            "duty_creation_failed",
            user_id=user_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise
```

### Пропагация Trace ID в gRPC-вызовах

При межсервисном взаимодействии через gRPC передавайте trace_id и correlation_id:

```python
import grpc
from contextvars import ContextVar

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class AuthGrpcClient:
    """gRPC клиент с трассировкой."""

    async def validate_token(self, token: str) -> ValidateTokenResponse:
        """Валидировать JWT-токен с передачей trace_id."""
        metadata = (
            ("x-trace-id", trace_id_var.get()),
            ("x-correlation-id", correlation_id_var.get()),
        )

        try:
            request = ValidateTokenRequest(token=token)
            response = await self._stub.ValidateToken(
                request,
                timeout=5.0,
                metadata=metadata,
            )
            return response
        except grpc.aio.AioRpcError as e:
            logger.error(
                "grpc_validate_token_failed",
                grpc_code=e.code().name,
                grpc_details=e.details(),
                exc_info=True,
            )
            raise
```

### Интеграция с Loki

Логи отправляются в Grafana Loki для централизованного хранения и анализа.

**Конфигурация Python Logging Handler для Loki:**
```python
# src/logging_config.py
import logging
import structlog
from logging_loki import LokiHandler


def configure_logging(service_name: str, loki_url: str) -> None:
    """Настроить логирование с отправкой в Loki."""

    # Настройка Python logging
    loki_handler = LokiHandler(
        url=f"{loki_url}/loki/api/v1/push",
        tags={"service": service_name},
        version="1",
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[loki_handler],
    )

    # Настройка structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# В main.py
from src.logging_config import configure_logging
from src.config import settings

configure_logging(
    service_name=settings.app_name,
    loki_url=settings.loki_url,
)
```

**Переменные окружения:**
```python
# src/config.py
class Settings(BaseSettings):
    # ...existing code...

    # Logging
    loki_url: str = "http://loki:3100"
    log_level: str = "INFO"
```

### Метрики для Prometheus

Экспортируйте метрики для мониторинга в Prometheus/Grafana:

```python
from prometheus_client import Counter, Histogram, make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator

# Кастомные метрики
duties_created_total = Counter(
    "duties_created_total",
    "Total number of duties created",
    ["building", "status"],
)

request_duration_seconds = Histogram(
    "request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "status_code"],
)


# В main.py
app = FastAPI(title="Duty Service")

# Автоматическая инструментация
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Монтирование метрик
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Использование кастомных метрик
@router.post("/duties")
async def create_duty(data: DutyCreateRequest) -> DutyResponse:
    duty = await duty_service.create_duty(data)
    duties_created_total.labels(
        building=duty.building,
        status=duty.status,
    ).inc()
    return DutyResponse.model_validate(duty)
```

### Уровни логирования

| Уровень    | Использование                                             |
|------------|-----------------------------------------------------------|
| `DEBUG`    | Детальная отладочная информация (только в development)    |
| `INFO`     | Успешные операции, ключевые бизнес-события                |
| `WARNING`  | Подозрительные ситуации, не критичные проблемы             |
| `ERROR`    | Ошибки, требующие внимания, с stack trace                  |
| `CRITICAL` | Критические сбои (недоступность БД, внешних сервисов)      |

### Docker Compose конфигурация для observability

```yaml
version: "3.9"

services:
  # ...existing services...

  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - loki_data:/loki

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - loki
      - prometheus

volumes:
  loki_data:
  prometheus_data:
  grafana_data:
```

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8001']
    metrics_path: '/metrics'

  - job_name: 'patrol-service'
    static_configs:
      - targets: ['patrol-service:8002']
    metrics_path: '/metrics'

  - job_name: 'duty-service'
    static_configs:
      - targets: ['duty-service:8003']
    metrics_path: '/metrics'

  - job_name: 'coworking-service'
    static_configs:
      - targets: ['coworking-service:8004']
    metrics_path: '/metrics'

  - job_name: 'application-service'
    static_configs:
      - targets: ['application-service:8005']
    metrics_path: '/metrics'
```
