# Gateway BFF

Single HTTP entry point for the campus application. Uses nginx as reverse proxy to:
- Proxy REST API at `/api/v1/applications` → application-service (via gRPC)
- Proxy REST API at `/api/v1/patrols` → patrol-service (via gRPC)

Both backend services are called via gRPC for type-safe communication.

- **Port:** 80 (exposed by nginx)
- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc
- **Health:** GET /health/liveness (for orchestrator)

## Configuration

- `APPLICATION_GRPC_URL` — application-service gRPC address (default: `application-service:50055`)
- `PATROL_GRPC_URL` — patrol-service gRPC address (default: `patrol-service:50052`)

## Services

| Path | Backend Service | Protocol |
|------|----------------|----------|
| `/api/v1/applications/*` | application-service:50055 | gRPC |
| `/api/v1/patrols/*` | patrol-service:50052 | gRPC |

## Auth (placeholder)

Authorization: Bearer &lt;JWT&gt; is required. The gateway currently parses the JWT payload (without signature verification) to get `sub` (user_id) and `roles`, and passes them to backend services via gRPC metadata. Replace with auth-service gRPC `ValidateToken` when available.

## Run locally

```bash
pip install -r requirements.txt
# Generate gRPC client (if not already in app/grpc_gen):
# python -m grpc_tools.protoc -I proto --python_out=app/grpc_gen --grpc_python_out=app/grpc_gen proto/application.proto
# python -m grpc_tools.protoc -I proto --python_out=app/grpc_gen --grpc_python_out=app/grpc_gen proto/patrol.proto
# Run uvicorn (nginx will be started separately in Docker)
uvicorn app.main:app --reload --port 8080
```

## Docker

```bash
docker build -t gateway .
docker run -p 8080:80 -e APPLICATION_GRPC_URL=host.docker.internal:50055 -e PATROL_GRPC_URL=host.docker.internal:50052 gateway
```
