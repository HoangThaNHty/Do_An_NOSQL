"""Đo cùng payload; chuẩn bị và kiểm tra kết quả ngoài vùng bấm giờ.

python data/benchmark.py --n 200 --http http://127.0.0.1:5000 --rtt 50
RTT là tình huống mô phỏng riêng; mặc định --rtt 0 chỉ đo thực tế cục bộ.
"""
import argparse
import csv
import json
import math
import platform
import statistics
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from pathlib import Path

import redis
import requests
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import config
from models import article as article_model
from services.cache_service import CacheService

RESULT_FILE = Path(__file__).resolve().parent / "result_benchmark.json"


class BenchmarkError(ValueError):
    pass


def _stats(values):
    ordered = sorted(values)
    if not ordered:
        raise BenchmarkError("Cần ít nhất một mẫu đo.")
    return {"count": len(values), "min": round(ordered[0], 6), "max": round(ordered[-1], 6),
            "avg": round(statistics.mean(values), 6), "median": round(statistics.median(values), 6),
            "p95": round(ordered[math.ceil(len(values) * .95) - 1], 6),
            "stdev": round(statistics.pstdev(values), 6)}


def _paired(readers, expected, n, warmup=10, prepare=None, validate=None):
    """Đảo thứ tự hai nguồn mỗi vòng; không tính prepare/validation vào thời gian."""
    samples = {name: [] for name in readers}
    names = list(readers)
    for iteration in range(warmup + n):
        order = names if iteration % 2 == 0 else list(reversed(names))
        for name in order:
            if prepare and name in prepare:
                prepare[name]()
            start = time.perf_counter()
            actual = readers[name]()
            elapsed = (time.perf_counter() - start) * 1000
            if validate and name in validate:
                actual = validate[name](actual)
            if actual != expected:
                raise BenchmarkError(f"Payload {name} thay đổi hoặc không tương đương; hủy phép đo.")
            if iteration >= warmup:
                samples[name].append(elapsed)
    return {name: _stats(times) for name, times in samples.items()}, samples


def _article_payload(doc):
    if not doc:
        raise BenchmarkError("Bài được chọn không còn tồn tại.")
    # Project Mongo's native types directly: no artificial JSON encode/decode on
    # the DB side. Redis needs JSON decoding only for fields stored as JSON.
    data = article_model.to_dict(doc)
    defaults = {"_id": "", "slug": "", "author": None, "seed_version": None,
                "title": "", "summary": "", "content": "", "image": "",
                "image_alt": "", "image_caption": "", "category": "", "tags": [],
                "author_name": "", "status": "published", "created_at": "", "updated_at": ""}
    return {key: data.get(key, default) for key, default in defaults.items()}


def _list_payload(db):
    result = article_model.list_articles(db, page=1, per_page=9, sort="newest")
    result["items"] = [_article_payload(doc) for doc in result["items"]]
    return result


def _http_fetch(session, url):
    response = session.get(url, timeout=15)
    return response, response.json()


def _validate_http(value, source):
    response, body = value
    response.raise_for_status()
    if body.get("success") is not True or body.get("source") != source:
        raise BenchmarkError(f"HTTP không phải {source}: không chấp nhận mẫu sai source/status.")
    return body["data"]


def _http_read(session, url, source):
    return _validate_http(_http_fetch(session, url), source)


def run(n=200, rtt_ms=0, http_host=None, output=RESULT_FILE, warmup=10, allow_simulated_http=False):
    if n < 1 or warmup < 0 or rtt_ms < 0:
        raise BenchmarkError("n phải dương; warmup và RTT không được âm.")
    output = Path(output)
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB,
                    password=config.REDIS_PASSWORD, socket_timeout=5)
    db = client[config.MONGO_DB_NAME]
    run_id = uuid.uuid4().hex
    detail_key, list_key = f"benchmark:{run_id}:detail", f"benchmark:{run_id}:list"
    scenarios, raw_samples = {}, {}
    session = requests.Session()
    try:
        r.ping()
        chosen = db.articles.find_one({"status": "published"}, sort=[("_id", 1)])
        if not chosen:
            raise BenchmarkError("Không có bài published để đo.")
        article_id = str(chosen["_id"])
        detail = _article_payload(chosen)
        listing = _list_payload(db)
        r.hset(detail_key, mapping=CacheService._article_mapping(article_id, chosen))
        r.expire(detail_key, 600)
        r.set(list_key, json.dumps(listing, ensure_ascii=False), ex=600)

        def mongo_detail():
            return _article_payload(db.articles.find_one({"_id": chosen["_id"]}))

        def redis_detail():
            return article_model.to_dict(CacheService._decode_hash(r.hgetall(detail_key)))

        def add(name, label, readers, expected, prepare=None, validate=None, **metadata):
            stats, samples = _paired(readers, expected, n, warmup, prepare, validate)
            payload = json.dumps(expected, ensure_ascii=False, sort_keys=True).encode("utf-8")
            scenarios[name] = {"label": label, "payload_bytes": len(payload),
                               "payload_verified": True, **stats, **metadata}
            raw_samples[name] = samples
            print(f"{label}: {stats['mongodb']['avg']:.3f} ms / {stats['redis']['avg']:.3f} ms")

        add("article_detail", "Nội dung một bài (DTO)",
            {"mongodb": mongo_detail, "redis": redis_detail}, detail,
            layer="data", simulated_db_latency_ms=0)
        add("article_list", "Danh sách 9 bài và phân trang",
            {"mongodb": lambda: _list_payload(db), "redis": lambda: json.loads(r.get(list_key))}, listing,
            layer="data", simulated_db_latency_ms=0, item_count=len(listing["items"]))

        if rtt_ms:
            def simulated_detail():
                time.sleep(rtt_ms / 1000)
                return mongo_detail()
            add("article_detail_network", f"MÔ PHỎNG: MongoDB thêm {rtt_ms} ms",
                {"mongodb": simulated_detail, "redis": redis_detail}, detail,
                layer="simulation", simulated_db_latency_ms=rtt_ms)

        http_metadata = None
        if http_host:
            base = http_host.rstrip("/")
            health = session.get(base + "/api/health", timeout=10)
            health.raise_for_status()
            info = health.json()
            if info.get("mongo_db") != config.MONGO_DB_NAME or info.get("redis_db") != config.REDIS_DB:
                raise BenchmarkError("App HTTP và CLI phải cùng MongoDB/Redis DB; hãy nạp lại app phiên bản mới.")
            latency = info.get("simulated_db_latency_ms")
            if latency is None or (latency != 0 and not allow_simulated_http):
                raise BenchmarkError("HTTP có mô phỏng hoặc thiếu thông tin latency. Tắt mô phỏng/restart, hoặc chỉ định --allow-simulated-http.")
            url = base + "/api/articles/" + article_id
            cache_key = CacheService.article_key(article_id)

            def miss_prepare():
                # Outside timer: a cache MISS should not include the DEL command.
                r.delete(cache_key)

            def hit_prepare():
                # Establish a valid full cache; source verified, outside timer.
                body = session.get(url, timeout=15)
                body.raise_for_status()
                if body.json().get("source") not in ("database", "cache"):
                    raise BenchmarkError("Không chuẩn bị được cache HTTP.")

            miss_prepare()
            expected = _http_read(session, url, "database")
            if _http_read(session, url, "cache") != expected:
                raise BenchmarkError("HTTP MISS/HIT trả payload khác nhau.")
            label = "HTTP: cache MISS / HIT" if latency == 0 else f"HTTP MÔ PHỎNG {latency} ms: MISS / HIT"
            add("http_request", label,
                {"mongodb": lambda: _http_fetch(session, url),
                 "redis": lambda: _http_fetch(session, url)}, expected,
                {"mongodb": miss_prepare, "redis": hit_prepare},
                {"mongodb": lambda value: _validate_http(value, "database"),
                 "redis": lambda value: _validate_http(value, "cache")},
                layer="http", simulated_db_latency_ms=latency)
            http_metadata = {"base_url": base, "article_id": article_id, "simulated_db_latency_ms": latency,
                             "source_checked_every_sample": True, "includes_json_decode": True}

        result = {"schema_version": 2,
                  "recorded_at": datetime.now(timezone(timedelta(hours=7))).isoformat(),
                  "environment": {"python": platform.python_version(), "platform": platform.platform(),
                      "mongodb": client.server_info()["version"], "redis": r.info("server")["redis_version"],
                      "flask": version("flask"), "pymongo": version("pymongo"), "redis_py": version("redis"),
                      "mongo_db": config.MONGO_DB_NAME, "redis_db": config.REDIS_DB,
                      "article_count": db.articles.count_documents({}), "n_per_source": n,
                      "warmup_per_source": warmup, "http": http_metadata},
                  "methodology": ["Hai nguồn trả cùng DTO; xác nhận ở từng mẫu sau khi dừng đồng hồ.",
                      "Đảo thứ tự đo mỗi vòng; warm-up riêng; lưu mọi mẫu thô và p95 nearest-rank.",
                      "Chuẩn bị/xóa cache nằm ngoài vùng bấm giờ; HTTP kiểm tra status và source.",
                      "Lớp dữ liệu đo đọc + chuyển đổi; HTTP đo trọn request và giải mã JSON.",
                      "Mô phỏng được ghi thành kịch bản riêng; không suy ra thời gian Redis từ tổng HTTP.",
                      "Tìm kiếm hiện không cache trong app nên không đưa cache tìm kiếm giả định vào bảng."],
                  "scenarios": scenarios, "samples_ms": raw_samples}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        with output.with_suffix(".csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["scenario", "source", "iteration", "milliseconds"])
            for scenario, samples in raw_samples.items():
                for source, values in samples.items():
                    writer.writerows((scenario, source, i + 1, f"{value:.6f}") for i, value in enumerate(values))
        print(f"JSON: {output}; mẫu thô CSV: {output.with_suffix('.csv')}")
        return result
    finally:
        # Only scratch keys created by this run, not user sessions/views/cache DB.
        r.delete(detail_key, list_key)
        session.close()
        r.close()
        client.close()


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--rtt", type=int, default=0)
    parser.add_argument("--http")
    parser.add_argument("--allow-simulated-http", action="store_true")
    parser.add_argument("--output", type=Path, default=RESULT_FILE)
    args = parser.parse_args()
    run(args.n, args.rtt, args.http, args.output, args.warmup, args.allow_simulated_http)


if __name__ == "__main__":
    main()
