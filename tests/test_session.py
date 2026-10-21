"""
tests/test_session.py - KIEM THU QUAN LY PHIEN DANG NHAP (Redis Hash + TTL)

Kiem tra:
    - Tao session -> sinh key Hash `session:<sid>` co TTL
    - Doc session -> tra ve dung du lieu nguoi dung
    - Gia han TTL (sliding expiration)
    - Xoa session -> key bi xoa khoi Redis
    - TTL dem lui theo thoi gian

Chay:  python -m pytest tests/ -v
"""

import sys
import time
from pathlib import Path

import pytest
import redis

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402
from services.session_service import SessionService  # noqa: E402

USER = {
    "_id": "68f000000000000000000001",
    "username": "sv1_admin",
    "email": "sv1@uit.edu.vn",
    "full_name": "SV1 - Data Architect",
    "role": "admin",
}


@pytest.fixture(scope="module")
def r():
    client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
    )
    client.ping()
    yield client
    client.close()


@pytest.fixture
def session_service(r):
    service = SessionService(r, config)
    yield service
    for key in r.keys("session:test-*"):
        r.delete(key)


def test_create_session_makes_hash_with_ttl(session_service, r):
    session_id = session_service.create_session(USER, ip="127.0.0.1", user_agent="pytest")
    key = session_service.session_key(session_id)
    assert r.exists(key) == 1
    assert r.type(key).decode() == "hash"          # luu bang cau truc Hash
    assert r.ttl(key) > 0                          # co TTL
    data = r.hgetall(key)
    assert data[b"username"].decode() == "sv1_admin"
    assert data[b"role"].decode() == "admin"
    assert data[b"ip"].decode() == "127.0.0.1"


def test_get_session(session_service):
    session_id = session_service.create_session(USER)
    data = session_service.get_session(session_id)
    assert data is not None
    assert data["username"] == "sv1_admin"
    assert data["email"] == "sv1@uit.edu.vn"
    assert session_service.get_session("khong-ton-tai") is None
    assert session_service.get_session(None) is None


def test_ttl_counts_down(session_service, r):
    session_id = session_service.create_session(USER)
    key = session_service.session_key(session_id)
    r.expire(key, 5)
    ttl_before = session_service.get_ttl(session_id)
    time.sleep(1.5)
    ttl_after = session_service.get_ttl(session_id)
    assert ttl_after < ttl_before      # TTL dang dem lui


def test_refresh_session_extends_ttl(session_service, r):
    session_id = session_service.create_session(USER)
    key = session_service.session_key(session_id)
    r.expire(key, 20)
    assert session_service.refresh_session(session_id) is True
    assert r.ttl(key) > 20             # da gia han
    assert session_service.refresh_session("khong-ton-tai") is False


def test_destroy_session_removes_key(session_service, r):
    session_id = session_service.create_session(USER)
    key = session_service.session_key(session_id)
    assert session_service.destroy_session(session_id) is True
    assert r.exists(key) == 0
    assert session_service.get_session(session_id) is None


def test_list_and_count_sessions(session_service):
    session_service.create_session(USER)
    session_service.create_session(USER)
    assert session_service.count_sessions() >= 2
    items = session_service.list_sessions()
    assert len(items) >= 2
    assert all("ttl" in item for item in items)
