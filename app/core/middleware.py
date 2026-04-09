import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.request_logging import serialize_body, serialize_headers, should_capture_body


logger = logging.getLogger("app.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        settings = get_settings()
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        started_at = time.perf_counter()
        request_body = b""
        if should_capture_body(
            request.headers.get("content-type"),
            self._parse_content_length(request.headers.get("content-length")),
            settings.api_request_log_body_max_length,
        ):
            request_body = await request.body()
        request.state.request_id = request_id
        request.state.user_id = None
        if request_body:
            request._receive = self._build_receive(request_body)

        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        response_body = b""
        if should_capture_body(
            response.headers.get("content-type"),
            self._parse_content_length(response.headers.get("content-length")),
            settings.api_request_log_body_max_length,
        ):
            response_body = await self._read_response_body(response)
        logged_response = self._clone_response(response, response_body)

        logged_response.headers["x-request-id"] = request_id
        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": logged_response.status_code,
                "duration_ms": duration_ms,
            },
        )

        writer = getattr(request.app.state, "api_request_log_writer", None)
        if writer is not None and settings.api_request_logging_enabled:
            route = request.scope.get("route")
            writer.enqueue(
                {
                    "request_id": request_id,
                    "user_id": getattr(request.state, "user_id", None),
                    "method": request.method,
                    "path": request.url.path,
                    "query_string": request.url.query or None,
                    "route_template": getattr(route, "path", None),
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                    "request_headers": serialize_headers(request.headers.items()),
                    "request_body": serialize_body(request_body, settings.api_request_log_body_max_length),
                    "response_status_code": logged_response.status_code,
                    "response_headers": serialize_headers(logged_response.headers.items()),
                    "response_body": serialize_body(response_body, settings.api_request_log_body_max_length),
                    "duration_ms": duration_ms,
                    "error_message": None if logged_response.status_code < 500 else "Request failed",
                }
            )

        return logged_response

    @staticmethod
    def _build_receive(body: bytes) -> Callable[[], Awaitable[dict[str, object]]]:
        consumed = False

        async def receive() -> dict[str, object]:
            nonlocal consumed
            if consumed:
                return {"type": "http.request", "body": b"", "more_body": False}
            consumed = True
            return {"type": "http.request", "body": body, "more_body": False}

        return receive

    @staticmethod
    async def _read_response_body(response: Response) -> bytes:
        if getattr(response, "body", None) is not None:
            return bytes(response.body)

        body_chunks = [chunk async for chunk in response.body_iterator]
        return b"".join(body_chunks)

    @staticmethod
    def _clone_response(response: Response, body: bytes) -> Response:
        if not body and getattr(response, "body", None) is None:
            return response

        cloned_response = Response(
            content=body or bytes(getattr(response, "body", b"")),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=response.background,
        )
        return cloned_response

    @staticmethod
    def _parse_content_length(value: str | None) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None
