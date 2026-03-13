from src.grpc_clients.auth_client import AuthClientProtocol, get_auth_client
from src.grpc_clients.application_client import ApplicationClientProtocol, get_application_client

__all__ = [
    "AuthClientProtocol",
    "get_auth_client",
    "ApplicationClientProtocol",
    "get_application_client",
]
