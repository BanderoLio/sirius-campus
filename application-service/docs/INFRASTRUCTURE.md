# Инфраструктура application-service

Описание зависимостей сервиса, переменных окружения, портов, health checks и способа запуска (Docker).

---

## 1. Зависимости сервиса

| Компонент | Назначение |
|-----------|------------|
| **PostgreSQL 15+** | База данных application_db. Доступ только из application-service (Database per Service). |
| **MinIO** | S3-совместимое хранилище для файлов заявлений (скан, голосовое сообщение, письмо родителя). Bucket создаётся при первом запуске или скриптом инициализации. |
| **auth-service (gRPC)** | Валидация JWT (ValidateToken) и получение данных пользователя (GetUserInfo). Обязательная зависимость для авторизации и обогащения данных. |
| **Redis** | По ТЗ-0 указан в стеке; для MVP application-service может работать без Redis. При необходимости — кэш или сессии в последующих итерациях. |

---

## 2. Переменные окружения

| Переменная | Обязательность | Описание | Пример |
|------------|----------------|----------|--------|
| DATABASE_URL | Да | URL подключения к PostgreSQL (async driver) | postgresql+asyncpg://campus:campus_secret@postgres-application:5432/application_db |
| MINIO_ENDPOINT | Да | Адрес MinIO (без схемы) | minio:9000 |
| MINIO_ACCESS_KEY | Да | Access key MinIO | minioadmin |
| MINIO_SECRET_KEY | Да | Secret key MinIO | minioadmin |
| MINIO_BUCKET_APPLICATIONS | Нет | Имя bucket для файлов заявлений | applications (по умолчанию) |
| MINIO_SECURE | Нет | Использовать HTTPS | false |
| AUTH_GRPC_URL | Да | Адрес auth-service для gRPC | auth-service:50051 |
| LOG_LEVEL | Нет | Уровень логирования | INFO |
| LOKI_URL | Нет | URL для отправки логов в Loki | http://loki:3100 |
| APP_NAME | Нет | Имя сервиса для логов и метрик | application-service |

Для локальной разработки без auth-service можно использовать заглушку; AUTH_GRPC_URL тогда указывает на мок или тестовый сервер.

---

## 3. Порты

| Порт | Протокол | Назначение |
|------|----------|------------|
| 8005 | HTTP | REST API (/api/v1/applications, /health, /metrics) |
| 50055 | gRPC | ApplicationService (GetApprovedLeaves) для patrol-service |

---

## 4. Health checks

Каждый сервис обязан предоставлять (ТЗ-0, чек-лист):

| Endpoint | Назначение |
|----------|------------|
| GET /health/liveness | Сервис запущен (возврат 200 без проверки зависимостей). |
| GET /health/readiness | Сервис готов принимать трафик: проверка доступности БД и при необходимости MinIO. При недоступности зависимости — 503. |

Рекомендуется использовать единый префикс `/health` для всех сервисов.

---

## 5. Docker

**Образ:** собирается из `application-service/Dockerfile` (multi-stage: deps + runtime, Python 3.11, Poetry, uvicorn).

**Запуск:** в docker-compose сервис `application-service` зависит от `postgres-application` и `minio`. Зависимость от `auth-service` указывается при наличии; при разработке MVP auth может быть заглушкой или отдельно поднятым контейнером.

**Сети:** сервис входит в общую сеть docker-compose, чтобы обращаться к postgres-application, minio и auth-service по имени сервиса.

**Томы:** данные не хранятся в контейнере application-service (БД и файлы — в postgres и minio). При необходимости можно монтировать конфиг или логи.

---

## 6. Хранение файлов (MinIO)

- Bucket: значение `MINIO_BUCKET_APPLICATIONS` (по умолчанию `applications`).
- Структура ключей: например `{application_id}/{document_id}.{ext}` или `{application_id}/{document_type}_{document_id}.{ext}` для однозначности и удобства очистки.
- Ограничения по типам и размерам файлов задаются в коде (application layer): PDF/JPG/PNG для скан, MP3/M4A/WAV для голоса; максимальный размер (например 10 MB для скан, 5 MB для голоса) и при необходимости проверка длительности аудио.

---

## 7. История и архивация (BR-EXIT-007)

Система хранит историю заявлений минимум 1 год. Реализуется хранением записей в БД без удаления. Политику архивации (перенос в холодное хранилище или удаление после N лет) при необходимости описать отдельно и реализовать фоновой задачей.
