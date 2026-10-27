"""Demo khóa với nhiều yêu cầu: chỉ một lần đọc MongoDB, Redis chia sẻ kết quả.

Delay là mô phỏng công việc chậm để dễ quan sát khóa, không phải benchmark DB.
Chỉ tạo key riêng cho lần demo; không sửa bài, phiên hay bộ đếm lượt xem.
"""
import argparse
import json
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import redis
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import config
from models import article as article_model
from services.cache_service import CacheService


def run(workers=12, delay_ms=1000, output=None):
    if workers < 2 or workers > 64 or not 0 <= delay_ms < config.CACHE_LOCK_WAIT_MS - 100:
        raise ValueError("Cần 2–64 yêu cầu; delay phải nhỏ hơn thời gian chờ khóa ít nhất 100ms.")
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)
    mongo = MongoClient(config.MONGO_URI)
    article = mongo[config.MONGO_DB_NAME].articles.find_one({"status": "published"}, {"_id": 1})
    if not article:
        raise ValueError("Cần một bài đã xuất bản.")
    cache = CacheService(r, config)
    identifier = "demo-lock-" + uuid.uuid4().hex
    for attr in ("KEY_HITS", "KEY_MISSES", "KEY_LOCK_WAITS", "KEY_LOCK_TIMEOUTS"):
        setattr(cache, attr, identifier + ":" + attr)
    key = cache.article_key(identifier)
    lock = cache.lock_key(key)
    barrier, guard = threading.Barrier(workers), threading.Lock()
    calls, observed_ttl = 0, None

    def load():
        nonlocal calls, observed_ttl
        with guard:
            calls += 1
        observed_ttl = r.pttl(lock)
        print(f"Đang giữ {lock}; PTTL={observed_ttl}ms; mô phỏng công việc {delay_ms}ms", flush=True)
        doc = article_model.get_article(mongo[config.MONGO_DB_NAME], str(article["_id"]))
        time.sleep(delay_ms / 1000)
        return article_model.to_dict(doc)

    def request():
        barrier.wait()
        return cache.get_article(identifier, load)[1]

    try:
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            sources = list(pool.map(lambda _: request(), range(workers)))
        result = {"recorded_at": datetime.now(timezone(timedelta(hours=7))).isoformat(),
                  "workers": workers, "loader_calls": calls, "database_responses": sources.count("database"),
                  "cache_responses": sources.count("cache"), "waits": int(r.get(cache.KEY_LOCK_WAITS) or 0),
                  "timeouts": int(r.get(cache.KEY_LOCK_TIMEOUTS) or 0), "lock_pttl_observed_ms": observed_ttl,
                  "lock_removed_afterwards": not r.exists(lock), "simulated_work_ms": delay_ms,
                  "wall_time_ms": round((time.perf_counter() - started) * 1000, 3),
                  "note": "Delay mô phỏng để quan sát; không phải số đo hiệu năng MongoDB."}
        assert calls == 1 and sources.count("database") == 1 and sources.count("cache") == workers - 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if output:
            Path(output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result
    finally:
        r.delete(key, lock, cache.KEY_HITS, cache.KEY_MISSES, cache.KEY_LOCK_WAITS, cache.KEY_LOCK_TIMEOUTS)
        r.close()
        mongo.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--delay-ms", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "result_lock_demo.json")
    args = parser.parse_args()
    run(args.workers, args.delay_ms, args.output)
