FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl nginx && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate gRPC client from proto at build time
RUN pip install grpcio-tools -q && \
    python -m grpc_tools.protoc -I proto --python_out=app/grpc_gen --grpc_python_out=app/grpc_gen proto/application.proto && \
    python -m grpc_tools.protoc -I proto --python_out=app/grpc_gen --grpc_python_out=app/grpc_gen proto/patrol.proto

EXPOSE 80

# Use nginx as reverse proxy in front of uvicorn
CMD ["/bin/sh", "-c", "uvicorn app.main:app --host 127.0.0.1 --port 8080 && nginx -g 'daemon off;'"]
