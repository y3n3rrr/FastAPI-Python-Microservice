import json
import logging
import queue
import threading
from collections.abc import Iterable

from sqlalchemy import text

from app.core.config import Settings
from app.db.session import get_engine

logger = logging.getLogger("app.request.db")

_STOP = object()
_SENSITIVE_FIELDS = {"authorization", "cookie", "set-cookie", "password", "password_hash", "access_token"}
_TEXT_CONTENT_TYPES = (
    "application/json",
    "application/problem+json",
    "application/x-www-form-urlencoded",
    "text/",
)


def redact_value(value: object) -> object:
    if isinstance(value, dict):
        redacted: dict[str, object] = {}
        for key, item in value.items():
            if key.lower() in _SENSITIVE_FIELDS:
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = redact_value(item)
        return redacted

    if isinstance(value, list):
        return [redact_value(item) for item in value]

    return value


def truncate_text(value: str | None, max_length: int) -> str | None:
    if value is None or len(value) <= max_length:
        return value
    return f"{value[:max_length]}...[truncated]"


def serialize_headers(headers: Iterable[tuple[str, str]]) -> dict[str, str]:
    data = {key: value for key, value in headers}
    return redact_value(data)  # type: ignore[return-value]


def should_capture_body(content_type: str | None, content_length: int | None, max_length: int) -> bool:
    if not content_type:
        return content_length is None or content_length <= max_length * 4

    normalized = content_type.lower()
    is_textual = normalized.startswith(_TEXT_CONTENT_TYPES)
    if not is_textual:
        return False

    return content_length is None or content_length <= max_length * 4


def serialize_body(body: bytes | None, max_length: int) -> str | None:
    if not body:
        return None

    decoded = body.decode("utf-8", errors="replace").strip()
    if not decoded:
        return None

    try:
        payload = json.loads(decoded)
    except json.JSONDecodeError:
        return truncate_text(decoded, max_length)

    serialized = json.dumps(redact_value(payload), ensure_ascii=True)
    return truncate_text(serialized, max_length)


class ApiRequestLogWriter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.queue: queue.Queue[dict[str, object] | object] = queue.Queue(maxsize=settings.api_request_log_queue_size)
        self.thread = threading.Thread(target=self._run, name="api-request-log-writer", daemon=True)
        schema = settings.database_schema.replace('"', '""')
        self.insert_statement = text(
            f"""
            INSERT INTO "{schema}".api_request_logs (
                request_id,
                user_id,
                method,
                path,
                query_string,
                route_template,
                client_ip,
                user_agent,
                request_headers,
                request_body,
                response_status_code,
                response_headers,
                response_body,
                duration_ms,
                error_message
            ) VALUES (
                CAST(:request_id AS UUID),
                :user_id,
                :method,
                :path,
                :query_string,
                :route_template,
                CAST(:client_ip AS INET),
                :user_agent,
                CAST(:request_headers AS JSONB),
                :request_body,
                :response_status_code,
                CAST(:response_headers AS JSONB),
                :response_body,
                :duration_ms,
                :error_message
            )
            """
        )

    def start(self) -> None:
        if not self.thread.is_alive():
            self.thread.start()

    def stop(self) -> None:
        if self.thread.is_alive():
            self.queue.put(_STOP)
            self.thread.join(timeout=5)

    def enqueue(self, payload: dict[str, object]) -> None:
        try:
            self.queue.put_nowait(payload)
        except queue.Full:
            logger.warning("request log queue is full; dropping log entry")

    def _run(self) -> None:
        while True:
            item = self.queue.get()
            if item is _STOP:
                break

            batch: list[dict[str, object]] = [self._prepare(item)]

            while len(batch) < 50:
                try:
                    queued_item = self.queue.get_nowait()
                except queue.Empty:
                    break

                if queued_item is _STOP:
                    self.queue.put(_STOP)
                    break

                batch.append(self._prepare(queued_item))

            try:
                with get_engine(self.settings.database_url).begin() as connection:
                    connection.execute(self.insert_statement, batch)
            except Exception:
                logger.exception("failed to persist api request logs")

    def _prepare(self, payload: dict[str, object] | object) -> dict[str, object]:
        if not isinstance(payload, dict):
            raise TypeError("request log payload must be a dictionary")

        return {
            **payload,
            "request_headers": json.dumps(payload.get("request_headers")) if payload.get("request_headers") is not None else None,
            "response_headers": json.dumps(payload.get("response_headers")) if payload.get("response_headers") is not None else None,
        }
