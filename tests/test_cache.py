"""
tests/test_cache.py - KIEM THU TANG CACHE-ASPIDE

Kiem tra cac hanh vi co ban cua De tai 06:
    - Cache MISS -> doc DB goc -> ghi nguoc Redis kem TTL
    - Cache HIT  -> tra ve tu Redis, KHONG goi lai DB goc
    - TTL        -> ton tai va giam dan
    - Cache Invalidation -> xoa key khi sua/xoa bai viet
    - INCR       -> tang bo dem luot xem

Chay:  python -m pytest tests/ -v
"""

import sys
from pathlib import Path

import pytest
import redis

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402
from services.cache_service import CacheService  # noqa: E402


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
def cache(r):
    service = CacheService(r, config)
    service.reset_stats()
    yield service
    # don sach key cua test
    for key in r.keys("article:cache:test-*"):
        r.delete(key)
    for key in r.keys("article:views:test-*"):
        r.delete(key)


SAMPLE = {
    "_id": "test-1",
    "title": "Bai viet kiem thu cache",
    "summary": "Tom tat",
    "content": "Noi dung kiem thu cache",
    "image": "/static/images/news_001.jpg",
    "category": "Cong nghe",
    "tags": ["cache"],
    "author_name": "Tester",
    "status": "published",
    "created_at": "01/01/2026 00:00",
    "updated_at": "01/01/2026 00:00",
}


def test_cache_miss_then_write_to_redis(cache, r):
    calls = {"count": 0}

    def loader():
        calls["count"] += 1
        return dict(SAMPLE)

    data, source = cache.get_article("test-1", loader)
    assert source == "database"          # lan 1: MISS
    assert calls["count"] == 1
    assert r.exists("article:cache:test-1") == 1   # da ghi nguoc Redis
    assert r.ttl("article:cache:test-1") > 0          # da gan TTL


def test_cache_hit_does_not_call_loader(cache):
    calls = {"count": 0}

    def loader():
        calls["count"] += 1
        return dict(SAMPLE)

    cache.get_article("test-1", loader)   # MISS
    data, source = cache.get_article("test-1", loader)   # HIT
    assert source == "cache"
    assert calls["count"] == 1            # loader khong bi goi lai
    assert data["title"] == SAMPLE["title"]
    assert data["tags"] == ["cache"]      # Hash -> list khi decode


def test_cache_ttl_decreases(cache, r):
    cache.set_article("test-1", SAMPLE, ttl=100)
    ttl1 = r.ttl("article:cache:test-1")
    assert 0 < ttl1 <= 100
    r.expire("article:cache:test-1", 50)
    ttl2 = r.ttl("article:cache:test-1")
    assert ttl2 <= 50


def test_cache_invalidation(cache, r):
    cache.set_article("test-1", SAMPLE)
    assert r.exists("article:cache:test-1") == 1
    removed = cache.invalidate_article("test-1")
    assert removed >= 1
    assert r.exists("article:cache:test-1") == 0


def test_incr_views(cache, r):
    before = cache.get_views("test-1")
    after = cache.incr_views("test-1")
    assert after == before + 1
    assert int(r.get("article:views:test-1")) == after
    assert r.ttl("article:views:test-1") > 0


def test_stats_hit_miss(cache):
    cache.get_article("test-1", lambda: dict(SAMPLE))   # MISS
    cache.get_article("test-1", lambda: dict(SAMPLE))   # HIT
    stats = cache.get_stats()
    assert stats["misses"] >= 1
    assert stats["hits"] >= 1
    assert stats["total_keys"] > 0
