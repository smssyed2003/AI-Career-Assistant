from collections import deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from time import sleep

from app.core.config import settings


class LLMRateLimiter:
    """Small in-process limiter for free-tier LLM RPM protection."""

    def __init__(self):
        self._calls: deque[datetime] = deque()
        self._lock = Lock()

    def wait_for_slot(self) -> None:
        if not settings.llm_queue_enabled:
            return

        while True:
            with self._lock:
                now = datetime.now(timezone.utc)
                window_start = now - timedelta(seconds=60)
                while self._calls and self._calls[0] < window_start:
                    self._calls.popleft()

                if len(self._calls) < max(1, settings.llm_requests_per_minute):
                    self._calls.append(now)
                    return

                wait_seconds = max(0.25, 60 - (now - self._calls[0]).total_seconds())

            sleep(min(wait_seconds, 5))

    def status(self) -> dict:
        with self._lock:
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(seconds=60)
            while self._calls and self._calls[0] < window_start:
                self._calls.popleft()
            return {
                "enabled": settings.llm_queue_enabled,
                "requests_per_minute": settings.llm_requests_per_minute,
                "used_in_current_window": len(self._calls),
                "available_now": max(0, settings.llm_requests_per_minute - len(self._calls)),
            }


llm_rate_limiter = LLMRateLimiter()
