"""
database/restore.py - KHOI PHUC DU LIEU (MongoDB + Redis) tu file backup

Chay:  python database/restore.py database/exports/backup_YYYYmmdd_HHMMSS
         python database/restore.py --latest     (tu tim backup moi nhat)

Tuy chon:
    --drop   xoa du lieu hien tai truoc khi khoi phuc
"""

import argparse
import json
import sys
from pathlib import Path

import redis
from bson.json_util import loads as bson_loads
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402

EXPORT_DIR = config.DATABASE_FOLDER / "exports"


def restore_mongodb(db, backup_dir: Path, drop=False):
    """Khoi phuc cac collection tu file JSON (Extended JSON)."""
    restored = {}
    for path in sorted(backup_dir.glob("mongo_*.json")):
        name = path.stem.replace("mongo_", "")
        docs = bson_loads(path.read_text(encoding="utf-8"))
        if drop:
            db[name].delete_many({})
        if docs:
            db[name].insert_many(docs)
        restored[name] = len(docs)
        print(f"  + {name}: khoi phuc {len(docs)} document")
    return restored


def restore_redis(r, backup_dir: Path, drop=False):
    """Khoi phuc key Redis kem TTL (dung SET / HSET / RESTORE)."""
    path = backup_dir / "redis_keys.json"
    if not path.exists():
        print("  [!] Khong tim thay redis_keys.json")
        return 0
    items = json.loads(path.read_text(encoding="utf-8"))
    count = 0
    for item in items:
        key = item["key"]
        ttl = item.get("ttl", -1)
        if drop:
            r.delete(key)
        if item["type"] == "string":
            r.set(key, item["value"])
        elif item["type"] == "hash":
            r.hset(key, mapping=item["mapping"])
        elif "dump" in item:
            r.restore(key, 0, bytes.fromhex(item["dump"]))
        if ttl and ttl > 0:
            r.expire(key, ttl)
        count += 1
    print(f"  + Redis: khoi phuc {count} key")
    return count


def main():
    parser = argparse.ArgumentParser(description="Khoi phuc du lieu tu file backup")
    parser.add_argument("backup_dir", nargs="?", help="Thu muc backup can khoi phuc")
    parser.add_argument("--latest", action="store_true", help="Dung backup moi nhat")
    parser.add_argument("--drop", action="store_true", help="Xoa du lieu hien tai truoc")
    args = parser.parse_args()

    if args.latest or not args.backup_dir:
        candidates = sorted(EXPORT_DIR.glob("backup_*"))
        if not candidates:
            print("Khong tim thay thu muc backup nao trong", EXPORT_DIR)
            return
        backup_dir = candidates[-1]
    else:
        backup_dir = Path(args.backup_dir)
    if not backup_dir.is_absolute():
        backup_dir = EXPORT_DIR / backup_dir.name

    print("=" * 64)
    print("  RESTORE DU LIEU - De tai 06")
    print("=" * 64)
    print(f"Nguon : {backup_dir}")

    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[config.MONGO_DB_NAME]
    client.admin.command("ping")
    r = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
    )
    r.ping()

    print("\n[1/2] Restore MongoDB:")
    restore_mongodb(db, backup_dir, drop=args.drop)

    print("\n[2/2] Restore Redis:")
    restore_redis(r, backup_dir, drop=args.drop)

    print("\nKiem tra sau khi khoi phuc:")
    for name in db.list_collection_names():
        if not name.startswith("system."):
            print(f"  {name}: {db[name].count_documents({})} document")
    print(f"  Redis: {r.dbsize()} key")
    print("=" * 64)


if __name__ == "__main__":
    main()
