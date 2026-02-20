# Gateway BFF

Single HTTP entry point for the campus application. Exposes REST API at `/api/v1/applications` and calls application-service via gRPC.

- **Port:** 8080
- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc
- **Health:** GET /health/liveness (for orchestrator)

## Configuration

- `APPLICATION_GRPC_URL` — application-service gRPC address (default: `application-service:50055`)

## Auth (placeholder)

Authorization: Bearer &lt;JWT&gt; is required. The gateway currently parses the JWT payload (without signature verification) to get `sub` (user_id) and `roles`, and passes them to application-service via gRPC metadata. Replace with auth-service gRPC `ValidateToken` when available.

## Run locally

```bash
pip install -r requirements.txt
# Generate gRPC client (if not already in app/grpc_gen):
# python -m grpc_tools.protoc -I proto --python_out=app/grpc_gen --grpc_python_out=app/grpc_gen proto/application.proto
uvicorn app.main:app --reload --port 8080
```

## Docker

```bash
docker build -t gateway .
docker run -p 8080:8080 -e APPLICATION_GRPC_URL=host.docker.internal:50055 gateway
```
