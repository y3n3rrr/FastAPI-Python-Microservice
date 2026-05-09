import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.core.request_logging import ApiRequestLogWriter


logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.api_request_log_writer = None

    if settings.api_request_logging_enabled:
        writer = ApiRequestLogWriter(settings)
        writer.start()
        app.state.api_request_log_writer = writer

    try:
        yield
    finally:
        writer = getattr(app.state, "api_request_log_writer", None)
        if writer is not None:
            writer.stop()

def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods_list or ["*"],
        allow_headers=settings.cors_allow_headers_list or ["*"],
    )
    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            "unhandled exception",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
            },
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred.",
                "request_id": request_id,
            },
        )

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"service": settings.app_name, "environment": settings.environment}

    return app


app = create_app()
