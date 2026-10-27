"""Kiểm tra khóa trên Redis thật, có nhiều service cùng tranh quyền nạp cache."""
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest
import redis

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import config
from services.cache_service import CacheBusyError, CacheService


@pytest.fixture
def cache():
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)
    before = set(r.scan_iter())
    c = CacheService(r, SimpleNamespace(TTL_ARTICLE_CACHE=30, TTL_ARTICLE_CACHE_HOT=60,
                                     TTL_ARTICLE_LIST=20, TTL_VIEWS=60))
    prefix = "qa-lock:" + uuid.uuid4().hex
    for name in ("KEY_HITS", "KEY_MISSES", "KEY_LOCK_WAITS", "KEY_LOCK_TIMEOUTS", "KEY_LIST_VERSION"):
        setattr(c, name, prefix + ":" + name)
    c.test_id = prefix
    try:
        yield c
    finally:
        added = set(r.scan_iter()) - before
        if added:
            r.delete(*added)
        r.close()


def sample(identifier, title="Bản mới"):
    return {"_id": identifier, "title": title, "content": "Nội dung khóa kiểm thử", "tags": ["khóa"], "status": "published"}


@pytest.mark.parametrize("kind", ["article", "list"])
def test_many_services_only_one_loader(cache, kind):
    workers = 12
    barrier = threading.Barrier(workers)
    guard = threading.Lock()
    calls = 0

    def load():
        nonlocal calls
        with guard:
            calls += 1
        time.sleep(0.15)
        return sample(cache.test_id) if kind == "article" else {"items": [sample(cache.test_id)], "total": 1}

    def run():
        # Separate service instances: the mutex must be Redis, not a Python lock.
        c = CacheService(cache.redis, cache.config)
        for name in ("KEY_HITS", "KEY_MISSES", "KEY_LOCK_WAITS", "KEY_LOCK_TIMEOUTS", "KEY_LIST_VERSION"):
            setattr(c, name, getattr(cache, name))
        barrier.wait()
        if kind == "article":
            return c.get_article(cache.test_id, load)
        return c.get_article_list(1, "newest", load, keyword=cache.test_id)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: run(), range(workers)))
    assert calls == 1
    assert [source for _, source in results].count("database") == 1
    assert [source for _, source in results].count("cache") == workers - 1
    assert int(cache.redis.get(cache.KEY_MISSES)) == 1
    assert int(cache.redis.get(cache.KEY_HITS)) == workers - 1
    assert int(cache.redis.get(cache.KEY_LOCK_WAITS)) > 0
    key = cache.article_key(cache.test_id) if kind == "article" else cache.list_key(1, "newest", keyword=cache.test_id)
    assert cache.redis.ttl(key) > 0
    assert not cache.redis.exists(cache.lock_key(key))


def test_loader_exception_releases_lock(cache):
    def fail():
        raise RuntimeError("loader failed")
    with pytest.raises(RuntimeError, match="loader failed"):
        cache.get_article(cache.test_id, fail)
    assert not cache.redis.exists(cache.lock_key(cache.article_key(cache.test_id)))
    assert cache.get_article(cache.test_id, lambda: sample(cache.test_id))[1] == "database"


def test_missing_article_releases_lock(cache):
    assert cache.get_article(cache.test_id, lambda: None) == (None, "none")
    assert not cache.redis.exists(cache.lock_key(cache.article_key(cache.test_id)))


def test_dead_owner_recovers_after_lease_expires(cache):
    key = cache.lock_key(cache.article_key(cache.test_id))
    cache.redis.set(key, "dead-owner", px=90)
    assert 0 < cache.redis.pttl(key) <= 90
    started = time.monotonic()
    assert cache.get_article(cache.test_id, lambda: sample(cache.test_id))[1] == "database"
    assert time.monotonic() - started >= 0.05
    assert not cache.redis.exists(key)


def test_wait_timeout_does_not_bypass_lock_and_hit_database(cache):
    key = cache.lock_key(cache.article_key(cache.test_id))
    cache.lock_wait_ms = 60
    cache.redis.set(key, "other-owner", px=1500)
    called = []
    started = time.monotonic()
    with pytest.raises(CacheBusyError):
        cache.get_article(cache.test_id, lambda: called.append(True))
    assert 0.04 <= time.monotonic() - started < 1
    assert not called
    assert cache.redis.get(key) == b"other-owner"


def test_release_cannot_delete_another_owners_lock(cache):
    key = cache.lock_key(cache.article_key(cache.test_id))
    cache.redis.set(key, "new-owner", px=1000)
    assert not cache._release_lock(key, "expired-owner")
    assert cache.redis.get(key) == b"new-owner"


def test_expired_owner_cannot_overwrite_newer_cache(cache):
    entered, resume = threading.Event(), threading.Event()
    cache.lock_ttl_ms = 90

    def old_loader():
        entered.set()
        assert resume.wait(3)
        return sample(cache.test_id, "Bản cũ")

    with ThreadPoolExecutor(max_workers=1) as pool:
        old = pool.submit(cache.get_article, cache.test_id, old_loader)
        assert entered.wait(2)
        deadline = time.monotonic() + 2
        key = cache.lock_key(cache.article_key(cache.test_id))
        while cache.redis.exists(key) and time.monotonic() < deadline:
            time.sleep(0.01)
        assert not cache.redis.exists(key)
        assert cache.get_article(cache.test_id, lambda: sample(cache.test_id))[0]["title"] == "Bản mới"
        resume.set()
        old.result(timeout=2)
    assert cache.get_article(cache.test_id, lambda: None)[0]["title"] == "Bản mới"


def test_invalidation_revokes_inflight_article_loader(cache):
    entered, resume = threading.Event(), threading.Event()

    def load():
        entered.set()
        assert resume.wait(3)
        return sample(cache.test_id, "Trước khi sửa")

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(cache.get_article, cache.test_id, load)
        assert entered.wait(2)
        cache.invalidate_article(cache.test_id)
        resume.set()
        future.result(timeout=2)
    assert not cache.redis.exists(cache.article_key(cache.test_id))


def test_list_invalidation_prevents_inflight_old_list_publish(cache):
    entered, resume = threading.Event(), threading.Event()
    def load():
        entered.set()
        assert resume.wait(3)
        return {"items": [sample(cache.test_id)]}
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(cache.get_article_list, 1, "newest", load, keyword=cache.test_id)
        assert entered.wait(2)
        cache.invalidate_lists()
        resume.set()
        future.result(timeout=2)
    assert not cache.redis.exists(cache.list_key(1, "newest", keyword=cache.test_id))
