"""In-memory rate limiter for login attempts."""
import time
import threading
import logging
from typing import Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AttemptRecord:
    """Track login attempts for a key."""
    attempts: int
    first_attempt: float
    locked_until: float = 0.0


class RateLimiter:
    """Thread-safe in-memory rate limiter.

    Tracks failed login attempts per IP+username key.
    After max_attempts within window_seconds, locks out for lockout_seconds.
    """

    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 300,  # 5 minutes
        lockout_seconds: int = 900  # 15 minutes
    ):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds
        self._records: Dict[str, AttemptRecord] = {}
        self._lock = threading.Lock()

    def _cleanup_expired(self) -> None:
        """Remove expired records (call while holding lock)."""
        now = time.time()
        expired_keys = []
        for key, record in self._records.items():
            # Remove if window expired and not locked
            if record.locked_until < now and (now - record.first_attempt) > self.window_seconds:
                expired_keys.append(key)
        for key in expired_keys:
            del self._records[key]

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """Check if a request is allowed.

        Args:
            key: Unique identifier (e.g., "ip:username")

        Returns:
            Tuple of (allowed: bool, retry_after_seconds: int)
            If allowed, retry_after is 0.
            If blocked, retry_after is seconds until lockout expires.
        """
        now = time.time()

        with self._lock:
            self._cleanup_expired()

            record = self._records.get(key)
            if not record:
                return True, 0

            # Check if locked out
            if record.locked_until > now:
                retry_after = int(record.locked_until - now) + 1
                return False, retry_after

            # Check if window expired - reset attempts
            if (now - record.first_attempt) > self.window_seconds:
                del self._records[key]
                return True, 0

            # Check if under limit
            if record.attempts < self.max_attempts:
                return True, 0

            return False, 0  # At limit but not locked (will be locked on next failed attempt)

    def record_attempt(self, key: str, success: bool) -> None:
        """Record a login attempt.

        Args:
            key: Unique identifier (e.g., "ip:username")
            success: Whether the login was successful
        """
        now = time.time()

        with self._lock:
            if success:
                # Clear on successful login
                self._records.pop(key, None)
                return

            record = self._records.get(key)

            if not record:
                # First failed attempt
                self._records[key] = AttemptRecord(
                    attempts=1,
                    first_attempt=now
                )
                return

            # Check if window expired - start fresh
            if (now - record.first_attempt) > self.window_seconds:
                self._records[key] = AttemptRecord(
                    attempts=1,
                    first_attempt=now
                )
                return

            # Increment attempts
            record.attempts += 1

            # Check if should lock out
            if record.attempts >= self.max_attempts:
                record.locked_until = now + self.lockout_seconds
                logger.warning(f"Rate limit exceeded for key '{key}', locked out for {self.lockout_seconds}s")


# Global login rate limiter instance
_login_limiter: RateLimiter = None


def get_login_limiter() -> RateLimiter:
    """Get the global login rate limiter instance."""
    global _login_limiter
    if _login_limiter is None:
        _login_limiter = RateLimiter()
    return _login_limiter
