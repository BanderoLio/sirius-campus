import os

APPLICATION_GRPC_URL = os.environ.get("APPLICATION_GRPC_URL", "application-service:50055")
PATROL_GRPC_URL = os.environ.get("PATROL_GRPC_URL", "patrol-service:50052")
LOKI_URL = os.environ.get("LOKI_URL", "").strip()
