"""
gRPC server implementation for auth-service.
"""
import uuid
from concurrent import futures
from typing import Optional

import grpc
from sqlalchemy import select

from src.core.config import get_settings
from src.core.database import async_session_factory
from src.core.security import decode_token
from src.models.database import Student, User, UserRole
from src.repositories.user import UserRepository

settings = get_settings()


class AuthServiceServicer:
    """gRPC Auth Service implementation."""

    async def ValidateToken(self, request, context):
        """Validate JWT token and get user data."""
        token = request.token

        if not token:
            return ValidateTokenResponse(valid=False)

        payload = decode_token(token)
        if not payload:
            return ValidateTokenResponse(valid=False)

        # Check if it's a refresh token
        if payload.get("type") == "refresh":
            return ValidateTokenResponse(valid=False)

        user_id = payload.get("sub")
        roles = payload.get("roles", [])
        building = payload.get("building")
        entrance = payload.get("entrance")
        floor = payload.get("floor")
        room = payload.get("room")

        return ValidateTokenResponse(
            valid=True,
            user_id=user_id,
            roles=roles,
            building=building or "",
            entrance=entrance or 0,
            floor=floor or 0,
            room=room or "",
        )

    async def GetUserInfo(self, request, context):
        """Get user info by ID."""
        user_id = request.user_id

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid user_id format")
            return UserInfoResponse()

        async with async_session_factory() as db:
            user_repo = UserRepository(db)
            user = await user_repo.get_by_id(user_uuid)

            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return UserInfoResponse()

            # Get user roles
            roles = [r.value for r in user.roles]

            # Get student profile data
            building = ""
            entrance = 0
            floor = 0
            room = ""
            is_minor = False

            if user.student_profile:
                student = user.student_profile
                building = str(student.building)
                entrance = student.entrance
                floor = student.floor
                room = str(student.room)
                is_minor = not student.is_adult

            return UserInfoResponse(
                user_id=str(user.id),
                last_name=user.last_name,
                first_name=user.first_name,
                patronymic=user.patronymic or "",
                building=building,
                entrance=entrance,
                floor=floor,
                room=room,
                roles=roles,
                phone=user.phone or "",
                email=user.email,
                is_minor=is_minor,
            )

    async def GetUsers(self, request, context):
        """Get list of users by filters."""
        building = request.building if request.building else None
        entrance = request.entrance if request.entrance else None
        floor = request.floor if request.floor else None
        room = request.room if request.room else None
        role = request.role if request.role else None
        page = request.page if request.page else 1
        size = request.size if request.size else 20

        async with async_session_factory() as db:
            user_repo = UserRepository(db)
            users, total = await user_repo.list_users(
                page=page,
                size=size,
                building=building,
                entrance=entrance,
                floor=floor,
            )

            user_responses = []
            for user in users:
                roles = [r.value for r in user.roles]

                # Get student profile data
                b = ""
                e = 0
                f = 0
                r = ""

                if user.student_profile:
                    b = str(user.student_profile.building)
                    e = user.student_profile.entrance
                    f = user.student_profile.floor
                    r = str(user.student_profile.room)

                user_responses.append(
                    UserInfoResponse(
                        user_id=str(user.id),
                        last_name=user.last_name,
                        first_name=user.first_name,
                        patronymic=user.patronymic or "",
                        building=b,
                        entrance=e,
                        floor=f,
                        room=r,
                        roles=roles,
                        phone=user.phone or "",
                        email=user.email,
                        is_minor=not user.student_profile.is_adult
                        if user.student_profile
                        else False,
                    )
                )

            pages = (total + size - 1) // size if size > 0 else 0

            return GetUsersResponse(
                users=user_responses,
                total=total,
                page=page,
                size=size,
                pages=pages,
            )

    async def CheckUserRole(self, request, context):
        """Check if user has a specific role."""
        user_id = request.user_id
        required_role = request.required_role

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid user_id format")
            return CheckUserRoleResponse(has_role=False)

        async with async_session_factory() as db:
            user_repo = UserRepository(db)
            user = await user_repo.get_by_id(user_uuid)

            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return CheckUserRoleResponse(has_role=False)

            user_roles = [r.value for r in user.roles]
            has_role = required_role in user_roles

            return CheckUserRoleResponse(has_role=has_role)


async def serve_grpc():
    """Start gRPC server."""
    from proto import auth_pb2_grpc

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{settings.GRPC_PORT}")
    await server.start()
    await server.wait_for_termination()


# Import generated proto modules (will be created by grpcio-tools)
try:
    from proto import auth_pb2
    from proto import auth_pb2_grpc

    ValidateTokenRequest = auth_pb2.ValidateTokenRequest
    ValidateTokenResponse = auth_pb2.ValidateTokenResponse
    GetUserInfoRequest = auth_pb2.GetUserInfoRequest
    UserInfoResponse = auth_pb2.UserInfoResponse
    GetUsersRequest = auth_pb2.GetUsersRequest
    GetUsersResponse = auth_pb2.GetUsersResponse
    CheckUserRoleRequest = auth_pb2.CheckUserRoleRequest
    CheckUserRoleResponse = auth_pb2.CheckUserRoleResponse
except ImportError:
    # Proto files not generated yet
    pass
