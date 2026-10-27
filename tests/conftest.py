"""Select a dedicated Redis test DB before test modules import config."""
import os

import pytest

try:
    test_redis_db = int(os.environ.get("TEST_REDIS_DB", "13"))
except ValueError as exc:
    raise pytest.UsageError("TEST_REDIS_DB phải là số DB Redis kiểm thử.") from exc
if not 1 <= test_redis_db <= 15:
    raise pytest.UsageError("Dùng TEST_REDIS_DB từ 1 đến 15, dành riêng kiểm thử; không dùng DB0.")
os.environ["REDIS_DB"] = str(test_redis_db)
