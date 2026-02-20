# application-service

Микросервис заявлений на выход (Кампус Сириус). REST API и gRPC (GetApprovedLeaves для patrol-service).

## Локальный запуск

**Требования:** Python 3.11+, Docker (для PostgreSQL и MinIO) или локальные PostgreSQL и MinIO.

1. Скопировать `.env.example` в `.env` и при необходимости изменить переменные.
2. Поднять зависимости (PostgreSQL, MinIO) через docker-compose из корня репозитория:
   ```bash
   docker-compose up -d postgres-application minio
   ```
   (Убедитесь, что Docker Desktop запущен.)
3. Установить зависимости и применить миграции:
   ```bash
   poetry install
   poetry run alembic upgrade head
   ```
   Без Poetry: `pip install -r requirements.txt` и `alembic upgrade head`.
4. Запуск сервера:
   ```bash
   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8005
   ```
   Без Poetry: `uvicorn src.main:app --host 0.0.0.0 --port 8005`.

## Тесты

```bash
poetry run pytest tests/ -v
# или без Poetry:
pip install -r requirements-dev.txt
python -m pytest tests/ -v
# или на Windows:
.\run_tests.ps1
```

## Генерация gRPC-кода

Для реализации gRPC-сервера (GetApprovedLeaves) сгенерируйте Python-модули из proto:

```bash
python -m grpc_tools.protoc -I proto --python_out=src/grpc_server --grpc_python_out=src/grpc_server proto/application.proto
```

После этого можно добавить запуск gRPC-сервера (порт 50055) в приложении или отдельным процессом.

## Документация

- [CONTRACTS](docs/CONTRACTS.md) — контракты (потребляемые и предоставляемые).
- [DATABASE](docs/DATABASE.md) — проектирование БД в 3НФ.
- [INFRASTRUCTURE](docs/INFRASTRUCTURE.md) — зависимости и переменные окружения.
