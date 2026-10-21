"""
database/seed_redis.py - NAP DU LIEU MAU TREN REDIS

Theo yeu cau cua De tai 06:
    "Redis: Toi thieu 20-50 Session/Cache Keys luu tai Redis co thiet lap TTL khac nhau."

Script nay tao ra cac nhom key voi TTL DAU NHAU de khi demo mo RedisInsight
nhin thay ngay su khac biet giua cac loai key:

    Nhom key                Kieu du lieu   TTL       So luong
    ------------------------ ------------- --------- ---------
    article:cache:<id>      Hash          300s      10
    article:cache:hot:<id>  Hash          1800s     5
    article:list:<p>:<s>    String (JSON) 60s       6
    article:views:<id>      String (dem)  86400s    15
    session:<sid>           Hash          1800s/var 12
    stats:cache:hits|misses String (dem)  khong TTL 2

Tong cong: ~50 key -> nam trong khoang 20-50 yeu cau.

Chay:  python database/seed_redis.py  [--reset]
"""

import argparse
import json
import secrets
import sys
from pathlib import Path

import redis
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402
from models import article as article_model  # noqa: E402

DEMO_SESSIONS = [
    ("sv1_admin", "SV1 - Data Architect", "admin", "127.0.0.1"),
    ("sv2_editor", "SV2 - Cache Specialist", "editor", "127.0.0.1"),
    ("sv3_editor", "SV3 - Fullstack Integrator", "editor", "127.0.0.1"),
    ("bien_tap", "Bien Tap", "editor", "127.0.0.1"),
    ("doc_giang_01", "Giang Vien", "admin", "127.0.0.1"),
    ("doc_giang_02", "Giang Vien", "admin", "127.0.0.1"),
    ("reader_01", "Nguoi Doc", "reader", "127.0.0.1"),
    ("reader_02", "Nguoi Doc", "reader", "127.0.0.1"),
    ("reader_03", "Nguoi Doc", "reader", "127.0.0.1"),
    ("reader_04", "Nguoi Doc", "reader", "127.0.0.1"),
    ("reader_05", "Nguoi Doc", "reader", "127.0.0.1"),
    ("reader_06", "Nguoi Doc", "reader", "127.0.0.1"),
]


def connect_redis():
    client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
        socket_connect_timeout=5,
    )
    client.ping()
    return client


def reset(r):
    """Xoa toan bo key cua du an (giu nguyen database khac)."""
    keys = r.keys("article:*") + r.keys("session:*") + r.keys("stats:*")
    if keys:
        r.delete(*keys)
    print(f"  Da xoa {len(keys)} key cu")


def seed_cache(r, db):
    """Tao cache bai viet (Hash) - lay noi dung that tu MongoDB de cache that."""
    articles = list(db["articles"].find().limit(21))
    if not articles:
        print("  [!] MongoDB chua co bai viet nao. Chay seed_articles.py truoc.")
        return 0

    count = 0
    for index, article in enumerate(articles):
        article_id = str(article["_id"])
        mapping = {
            "_id": article_id,
            "title": article.get("title", ""),
            "summary": article.get("summary", ""),
            "content": article.get("content", ""),
            "image": article.get("image", ""),
            "category": article.get("category", ""),
            "tags": json.dumps(article.get("tags", []), ensure_ascii=False),
            "author_name": article.get("author_name", ""),
            "status": article.get("status", "published"),
            "created_at": str(article.get("created_at", "")),
            "updated_at": str(article.get("updated_at", "")),
        }
        # 10 bai viet thuong: TTL 300s
        if index < 10:
            key = f"article:cache:{article_id}"
            ttl = config.TTL_ARTICLE_CACHE
        # 5 bai viet "nong": TTL 1800s
        elif index < 15:
            key = f"article:cache:hot:{article_id}"
            ttl = config.TTL_ARTICLE_CACHE_HOT
        else:
            continue
        r.hset(key, mapping=mapping)
        r.expire(key, ttl)
        count += 1

    # Bo dem luot xem (15 key) - tang bang INCR
    for article in articles[:15]:
        key = f"article:views:{article['_id']}"
        r.set(key, random_int(20, 500), ex=config.TTL_VIEWS)
        count += 1

    # Cache danh sach (6 key, TTL 60s) - dung du lieu THAT tu MongoDB
    for page in range(1, 7):
        key = f"article:list:{page}:newest:all-all"
        result = article_model.list_articles(db, page=page, per_page=9, sort="newest")
        items = [article_model.to_dict(doc) for doc in result["items"]]
        payload = {
            "items": items,
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_pages": result["total_pages"],
            "has_prev": result["has_prev"],
            "has_next": result["has_next"],
        }
        r.set(key, json.dumps(payload, default=str, ensure_ascii=False), ex=config.TTL_ARTICLE_LIST)
        count += 1

    return count


def random_int(low, high):
    import random

    return random.randint(low, high)


def seed_sessions(r):
    """Tao 12 phien dang nhap (Hash) voi TTL khac nhau de demo TTL dem lui."""
    count = 0
    for index, (username, full_name, role, ip) in enumerate(DEMO_SESSIONS):
        session_id = secrets.token_hex(32)
        key = f"session:{session_id}"
        # TTL khac nhau giua cac phien: 1800 / 900 / 600 / 300 ...
        ttl = [1800, 1800, 1800, 900, 900, 600, 600, 300, 300, 180, 120, 60][index % 12]
        mapping = {
            "session_id": session_id,
            "user_id": f"{index + 1:02d}",
            "username": username,
            "email": f"{username}@uit.edu.vn",
            "full_name": full_name,
            "role": role,
            "login_at": "2026-10-21 08:30:00",
            "ip": ip,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0",
        }
        r.hset(key, mapping=mapping)
        r.expire(key, ttl)
        count += 1
    return count


def seed_stats(r):
    """Dem so lieu Hit/Miss gia lap cho ban do lieu mau."""
    r.set("stats:cache:hits", 128, ex=None)
    r.set("stats:cache:misses", 37, ex=None)
    return 2


def main():
    parser = argparse.ArgumentParser(description="Nap du lieu mau len Redis")
    parser.add_argument("--reset", action="store_true", help="Xoa key cu truoc khi nap")
    args = parser.parse_args()

    print("=" * 64)
    print("  SEED DU LIEU MAU TREN REDIS - De tai 06")
    print("=" * 64)

    r = connect_redis()
    print(f"Redis     : {config.REDIS_HOST}:{config.REDIS_PORT} (db {config.REDIS_DB})")
    print(f"Phi ban   : {r.info('server')['redis_version']}")

    if args.reset:
        print("\n[0/3] Xoa du lieu cu:")
        reset(r)

    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[config.MONGO_DB_NAME]

    print("\n[1/3] Cache bai viet + bo dem luot xem:")
    n = seed_cache(r, db)
    print(f"  + {n} key (Hash article:cache, article:views, article:list)")

    print("\n[2/3] Session dang nhap (Hash):")
    n = seed_sessions(r)
    print(f"  + {n} key session:* voi TTL khac nhau (1800 -> 60 giay)")

    print("\n[3/3] Bo dem Hit/Miss:")
    n = seed_stats(r)
    print(f"  + {n} key stats:*")

    total = r.dbsize()
    print("\nKiem tra:")
    print(f"  Tong so key dang luu tren Redis: {total}")
    print("  Phan bo theo kieu du lieu:")
    types = {}
    for key in r.scan_iter(match="*", count=500):
        t = r.type(key).decode("utf-8")
        types[t] = types.get(t, 0) + 1
    for t, c in sorted(types.items()):
        print(f"    {t:8} : {c} key")
    print("\nMo Redis Insight -> Database 0 de xem truc tiep.")
    print("=" * 64)


if __name__ == "__main__":
    main()
