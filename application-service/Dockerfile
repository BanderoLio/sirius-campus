FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base AS deps
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only main

FROM base AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY . .

# Generate gRPC Python modules from proto at build time
RUN python -m grpc_tools.protoc -I proto --python_out=src/grpc_server --grpc_python_out=src/grpc_server proto/application.proto

EXPOSE 8005 50055

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]
