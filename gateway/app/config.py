import os

APPLICATION_GRPC_URL = os.environ.get("APPLICATION_GRPC_URL", "application-service:50055")
LOKI_URL = os.environ.get("LOKI_URL", "").strip()
