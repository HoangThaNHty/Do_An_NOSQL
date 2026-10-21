"""
scripts/benchmark.py - DO THOI GIAN DOC DU LIEU: MONGODB (DB goc) vs REDIS (CACHE)

Dung cho Chuong 8 (Kiem thu hieu nang) va buoc demo so sanh tren tab Network (F12).

3 kich ban duoc do:
    1. Chi tiet bai viet   : MongoDB find_one            vs Redis HGETALL
    2. Danh sach bai viet  : MongoDB find + count        vs Redis GET (JSON)
    3. Tim kiem           : MongoDB regex tren content  vs Redis GET (JSON da cache)

Ket qua duoc ghi ra file JSON (scripts/result_benchmark.json) de ve bieu do.

Chay:  python scripts/benchmark.py  [--n 200] [--host http://127.0.0.1:5000]
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import redis
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402
from models import article as article_model  # noqa: E402

RESULT_FILE = Path(__file__).resolve().parent / "result_benchmark.json"


def _measure(func, n, warmup=5):
    """Chay ham n lan va tra ve danh sach thoi gian (ms)."""
    for _ in range(warmup):
        func()
    times = []
    for _ in range(n):
        start = time.perf_counter()
        func()
        times.append((time.perf_counter() - start) * 1000)
    return times


def _stats(times):
    times_sorted = sorted(times)
    return {
        "count": len(times),
        "min": round(min(times), 3),
        "max": round(max(times), 3),
        "avg": round(statistics.mean(times), 3),
        "median": round(statistics.median(times), 3),
        "p95": round(times_sorted[int(len(times_sorted) * 0.95) - 1], 3),
        "stdev": round(statistics.pstdev(times), 3),
    }


def run(n=200, rtt_ms=50, http_host=None):
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[config.MONGO_DB_NAME]
    r = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
    )
    r.ping()

    articles = list(db["articles"].find().limit(20))
    if not articles:
        print("Chua co bai viet nao trong MongoDB. Chay seed_articles.py truoc.")
        return None
    article_id = str(articles[0]["_id"])

    # Dam bao co key cache de so sanh cong bang
    r.hset(f"article:cache:{article_id}", mapping={"_id": article_id, "title": articles[0]["title"]})
    r.expire(f"article:cache:{article_id}", config.TTL_ARTICLE_CACHE)
    r.set("article:list:1:newest:all-all", json.dumps({"items": []}), ex=config.TTL_ARTICLE_LIST)

    results = {}

    # ---------------- 1. Chi tiet bai viet ----------------
    print("\n[1/3] Chi tiet bai viet (find_one vs HGETALL)")
    t_mongo = _measure(lambda: db["articles"].find_one({"_id": articles[0]["_id"]}), n)
    t_redis = _measure(lambda: r.hgetall(f"article:cache:{article_id}"), n)
    results["article_detail"] = {"mongodb": _stats(t_mongo), "redis": _stats(t_redis)}
    print(f"   MongoDB: {results['article_detail']['mongodb']['avg']} ms")
    print(f"   Redis  : {results['article_detail']['redis']['avg']} ms")

    # ---------------- 2. Danh sach bai viet ----------------
    print("[2/3] Danh sach bai viet (find + count vs GET)")
    t_mongo = _measure(
        lambda: (list(db["articles"].find().sort("created_at", -1).limit(9)), db["articles"].count_documents({})),
        n,
    )
    t_redis = _measure(lambda: r.get("article:list:1:newest:all-all"), n)
    results["article_list"] = {"mongodb": _stats(t_mongo), "redis": _stats(t_redis)}
    print(f"   MongoDB: {results['article_list']['mongodb']['avg']} ms")
    print(f"   Redis  : {results['article_list']['redis']['avg']} ms")

    # ---------------- 3. Tim kiem ----------------
    print("[3/3] Tim kiem (regex tren content vs GET da cache)")
    t_mongo = _measure(lambda: list(db["articles"].find({"title": {"$regex": "cong", "$options": "i"}})), n)
    t_redis = _measure(lambda: r.get("article:list:1:newest:all-all"), n)
    results["search"] = {"mongodb": _stats(t_mongo), "redis": _stats(t_redis)}
    print(f"   MongoDB: {results['search']['mongodb']['avg']} ms")
    print(f"   Redis  : {results['search']['redis']['avg']} ms")

    # ---------------- 4. Mo phong do tre mang (RTT) ----------------
    # Khi MongoDB nam o MAY KHAC (cloud / may chay thu nghiem), moi lan doc
    # deu phai trai qua 1 lan round-trip mang. Day la kich ban mo phong do
    # tre mang 50ms - dung de kiem chung co so ly thuyet trong bao cao.
    rtt_seconds = rtt_ms / 1000
    print(f"[4/4] Mo phong do tre mang {rtt_ms}ms khi doc MongoDB tu may khac")

    def loader_with_rtt():
        time.sleep(rtt_seconds)
        return db["articles"].find_one({"_id": articles[0]["_id"]})

    t_mongo = _measure(loader_with_rtt, max(20, n // 10))
    t_redis = _measure(lambda: r.hgetall(f"article:cache:{article_id}"), max(20, n // 10))
    results["article_detail_network"] = {"mongodb": _stats(t_mongo), "redis": _stats(t_redis)}
    results["article_detail_network"]["simulated_rtt_ms"] = rtt_ms
    print(f"   MongoDB: {results['article_detail_network']['mongodb']['avg']} ms")
    print(f"   Redis  : {results['article_detail_network']['redis']['avg']} ms")

    # ---------------- 5. Do qua HTTP (cung voi tab Network F12) ----------------
    if http_host:
        import requests

        url = f"{http_host}/api/articles/{article_id}"
        print(f"[5/5] Do qua HTTP {url} (tuong duong tab Network cua Chrome)")

        def http_miss():
            r.delete(f"article:cache:{article_id}")
            requests.get(url, timeout=10)

        def http_hit():
            requests.get(url, timeout=10)

        t_miss = _measure(http_miss, max(30, n // 5))
        t_hit = _measure(http_hit, max(30, n // 5))
        results["http_request"] = {"mongodb": _stats(t_miss), "redis": _stats(t_hit)}
        print(f"   Cache MISS (doc MongoDB): {results['http_request']['mongodb']['avg']} ms")
        print(f"   Cache HIT  (doc Redis)  : {results['http_request']['redis']['avg']} ms")

    # ---------------- Ket qua ----------------
    results["note"] = (
        "Do o tren chay truc tiep trong cung mot may (bo qua do tre mang). "
        "Khi trien khai that tren may chu khac, do tre mang lam chenh lech lon hon."
    )
    results["n_requests"] = n
    results["mongo_db"] = config.MONGO_DB_NAME
    results["redis_version"] = r.info("server")["redis_version"]

    RESULT_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nKet qua luu tai: {RESULT_FILE}")

    print("\n" + "=" * 70)
    print(f"{'Kich ban':<34}{'MongoDB (ms)':>16}{'Redis (ms)':>14}{'Nhanh hon':>12}")
    print("-" * 70)
    for key, label in (
        ("article_detail", "Chi tiet bai viet"),
        ("article_list", "Danh sach bai viet"),
        ("search", "Tim kiem"),
        ("article_detail_network", f"Chi tiet (mo phong RTT {rtt_ms}ms)"),
        ("http_request", "HTTP request (nhu tab Network F12)"),
    ):
        if key not in results:
            continue
        m = results[key]["mongodb"]["avg"]
        c = results[key]["redis"]["avg"]
        factor = (m / c) if c else 0
        print(f"{label:<34}{m:>16.3f}{c:>14.3f}{('x%.1f' % factor):>12}")
    print("=" * 70)
    return results


def main():
    parser = argparse.ArgumentParser(description="Do hieu nang MongoDB vs Redis")
    parser.add_argument("--n", type=int, default=200, help="So lan do moi kich ban")
    parser.add_argument(
        "--rtt",
        type=int,
        default=50,
        help="Do tre mang mo phong (ms) khi doc MongoDB o may khac (mac dinh 50)",
    )
    parser.add_argument(
        "--http",
        default=None,
        help="Dia chi app dang chay, vd http://127.0.0.1:5000 (de do nhu tab Network F12)",
    )
    args = parser.parse_args()
    print("=" * 70)
    print("  BENCHMARK - De tai 06 (Cache-Aside)")
    print("=" * 70)
    run(args.n, rtt_ms=args.rtt, http_host=args.http)


if __name__ == "__main__":
    main()
