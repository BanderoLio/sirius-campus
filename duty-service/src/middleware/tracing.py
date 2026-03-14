import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.tracing import trace_id_var, correlation_id_var


class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        trace_id_var.set(trace_id)
        correlation_id_var.set(correlation_id)

        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Correlation-ID"] = correlation_id
        return response
