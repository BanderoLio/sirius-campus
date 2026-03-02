"""
gRPC client for patrol-service. Generated code (patrol_pb2, patrol_pb2_grpc)
is produced at build time into app/grpc_gen/.
"""
import sys
from pathlib import Path

import grpc

from app.config import PATROL_GRPC_URL

_grpc_gen = Path(__file__).resolve().parent / "grpc_gen"
if _grpc_gen.exists() and str(_grpc_gen) not in sys.path:
    sys.path.insert(0, str(_grpc_gen))

try:
    import patrol_pb2  # type: ignore[import-not-found]
    import patrol_pb2_grpc  # type: ignore[import-not-found]
except ImportError:
    patrol_pb2 = None
    patrol_pb2_grpc = None


def _metadata(user_id: str, roles: list[str]) -> list[tuple[str, str]]:
    return [
        ("x-user-id", user_id),
        ("x-user-roles", ",".join(roles)),
    ]


async def list_patrols(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    page: int = 1,
    size: int = 20,
    date: str | None = None,
    building: str | None = None,
    entrance: str | None = None,
    status: str | None = None,
):
    if patrol_pb2 is None or patrol_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = patrol_pb2_grpc.PatrolServiceStub(channel)
    req = patrol_pb2.ListPatrolsRequest(
        page=page,
        size=size,
        date=date or "",
        building=building or "",
        entrance=entrance or "",
        status=status or "",
    )
    return await stub.ListPatrols(req, metadata=_metadata(user_id, roles))


async def create_patrol(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    date: str,
    building: str,
    entrance: str,
):
    if patrol_pb2 is None or patrol_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = patrol_pb2_grpc.PatrolServiceStub(channel)
    req = patrol_pb2.CreatePatrolRequest(
        date=date,
        building=building,
        entrance=entrance,
    )
    return await stub.CreatePatrol(req, metadata=_metadata(user_id, roles))


async def get_patrol_details(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    patrol_id: str,
):
    if patrol_pb2 is None or patrol_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = patrol_pb2_grpc.PatrolServiceStub(channel)
    req = patrol_pb2.GetPatrolDetailsRequest(patrol_id=patrol_id)
    return await stub.GetPatrolDetails(req, metadata=_metadata(user_id, roles))


async def update_patrol(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    patrol_id: str,
    status: str,
):
    if patrol_pb2 is None or patrol_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = patrol_pb2_grpc.PatrolServiceStub(channel)
    req = patrol_pb2.UpdatePatrolRequest(
        patrol_id=patrol_id,
        status=status,
    )
    return await stub.UpdatePatrol(req, metadata=_metadata(user_id, roles))


async def delete_patrol(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    patrol_id: str,
):
    if patrol_pb2 is None or patrol_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = patrol_pb2_grpc.PatrolServiceStub(channel)
    req = patrol_pb2.DeletePatrolRequest(patrol_id=patrol_id)
    return await stub.DeletePatrol(req, metadata=_metadata(user_id, roles))


async def get_patrol_entry(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    patrol_id: str,
    patrol_entry_id: str,
):
    if patrol_pb2 is None or patrol_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = patrol_pb2_grpc.PatrolServiceStub(channel)
    req = patrol_pb2.GetPatrolEntryRequest(
        patrol_id=patrol_id,
        patrol_entry_id=patrol_entry_id,
    )
    return await stub.GetPatrolEntry(req, metadata=_metadata(user_id, roles))


async def update_patrol_entry(
    channel: grpc.aio.Channel,
    user_id: str,
    roles: list[str],
    patrol_id: str,
    patrol_entry_id: str,
    is_present: bool,
    absence_reason: str | None = None,
):
    if patrol_pb2 is None or patrol_pb2_grpc is None:
        raise RuntimeError("gRPC generated code not available")
    stub = patrol_pb2_grpc.PatrolServiceStub(channel)
    req = patrol_pb2.UpdatePatrolEntryRequest(
        patrol_id=patrol_id,
        patrol_entry_id=patrol_entry_id,
        is_present=is_present,
        absence_reason=absence_reason or "",
    )
    return await stub.UpdatePatrolEntry(req, metadata=_metadata(user_id, roles))


def get_channel() -> grpc.aio.Channel:
    return grpc.aio.insecure_channel(PATROL_GRPC_URL)
