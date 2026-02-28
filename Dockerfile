FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
FROM base AS deps
RUN pip install --no-cache-dir poetry
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only main

# Generate proto files
FROM base AS proto-builder
RUN pip install --no-cache-dir grpcio-tools
COPY proto/ ./proto/
RUN python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/auth.proto

# Final runtime image
FROM base AS runtime
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY --from=proto-builder /app/proto /app/proto
COPY . .

EXPOSE 8001 50051

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
