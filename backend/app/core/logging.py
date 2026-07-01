import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("primetrade")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        user = getattr(request.state, "user_email", "-")
        logger.info(
            "%s %s status=%d time=%.1fms user=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            user,
        )
        return response
