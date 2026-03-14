import asyncio
import importlib
import sys
from dataclasses import dataclass
from typing import Protocol, Sequence
from uuid import UUID

import grpc

from src.config import settings
from src.exceptions import AuthServiceUnavailableException, UnauthorizedException
from src.grpc import auth_pb2
from src.tracing import trace_id_var, correlation_id_var

sys.modules.setdefault("auth_pb2", auth_pb2)
auth_pb2_grpc = importlib.import_module("src.grpc.auth_pb2_grpc")


class AuthServiceStubProtocol(Protocol):
    async def ValidateToken(
        self,
        request: auth_pb2.ValidateTokenRequest,
        timeout: float,
        metadata: Sequence[tuple[str, str]],
    ) -> auth_pb2.ValidateTokenResponse:
        ...


@dataclass
class AuthenticatedUser:
    user_id: UUID
    roles: list[str]
    room_id: UUID | None


class AuthGrpcClient:
    def __init__(self) -> None:
        self._address = f"{settings.auth_service_host}:{settings.auth_service_port}"
        self._channel: grpc.aio.Channel | None = None
        self._stub: AuthServiceStubProtocol | None = None

    def _get_stub(self) -> AuthServiceStubProtocol:
        if self._stub is None:
            self._channel = grpc.aio.insecure_channel(self._address)
            self._stub = auth_pb2_grpc.AuthServiceStub(self._channel)
        return self._stub

    def _metadata(self) -> Sequence[tuple[str, str]]:
        return (
            ("x-trace-id", trace_id_var.get()),
            ("x-correlation-id", correlation_id_var.get()),
        )

    async def validate_token(self, token: str) -> AuthenticatedUser:
        stub = self._get_stub()
        request = auth_pb2.ValidateTokenRequest(token=token)
        retries = 3

        for attempt in range(retries):
            try:
                response = await stub.ValidateToken(
                    request,
                    timeout=settings.grpc_timeout_seconds,
                    metadata=self._metadata(),
                )
                if not response.valid:
                    raise UnauthorizedException("Invalid token")
                room_id = UUID(response.room_id) if response.room_id else None
                return AuthenticatedUser(
                    user_id=UUID(response.user_id),
                    roles=list(response.roles),
                    room_id=room_id,
                )
            except grpc.aio.AioRpcError as exc:
                if exc.code() == grpc.StatusCode.UNAUTHENTICATED:
                    raise UnauthorizedException("Invalid token") from exc
                if exc.code() == grpc.StatusCode.UNAVAILABLE and attempt < retries - 1:
                    await asyncio.sleep(0.1 * (2**attempt))
                    continue
                raise AuthServiceUnavailableException("Auth service unavailable") from exc
            except ValueError as exc:
                raise UnauthorizedException("Invalid token payload") from exc

        raise AuthServiceUnavailableException("Auth service unavailable")


_auth_client: AuthGrpcClient | None = None


def get_auth_client() -> AuthGrpcClient:
    global _auth_client
    if _auth_client is None:
        _auth_client = AuthGrpcClient()
    return _auth_client
