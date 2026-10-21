"""
data/backup.py - BACKUP DU LIEU (MongoDB + Redis)

Theo yeu cau thang diem muc 6: "Import/export du lieu; Backup va Restore du lieu"

Cach luu duoc dung trong du an:
    - MongoDB : xuat toan bo collection ra file JSON (Extended JSON) trong data/exports/
    - Redis   : luu key dang ton tai kem kieu du lieu + TTL vao file JSON
                (dung DUMP/RESTORE de giu nguyen nguyen ban, va van doc duoc file)

Chay:  python data/backup.py
Ket qua: data/exports/backup_<timestamp>/
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import redis
from bson.json_util import dumps as bson_dumps
from bson.json_util import loads as bson_loads
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402

EXPORT_DIR = config.DATA_FOLDER / "exports"


def backup_mongodb(db, out_dir: Path):
    """Xuat moi collection cua MongoDB ra file JSON (Extended JSON)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    for name in db.list_collection_names():
        if name.startswith("system."):
            continue
        docs = list(db[name].find())
        path = out_dir / f"mongo_{name}.json"
        path.write_text(bson_dumps(docs, indent=2, ensure_ascii=False), encoding="utf-8")
        result[name] = len(docs)
        print(f"  + mongo_{name}.json  ({len(docs)} document)")
    return result


def backup_redis(r, out_dir: Path):
    """
    Luu toan bo key dang ton tai tren Redis kem kieu du lieu va TTL.
    Dung cho lenh RESTORE de khoi phuc nguyen trang thai.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for key in r.scan_iter(match="*", count=1000):
        key_str = key.decode("utf-8") if isinstance(key, bytes) else key
        key_type = r.type(key).decode("utf-8")
        ttl = r.ttl(key)
        item = {"key": key_str, "type": key_type, "ttl": ttl}
        if key_type == "string":
            value = r.get(key)
            item["value"] = value.decode("utf-8") if isinstance(value, bytes) else value
        elif key_type == "hash":
            mapping = {}
            for k, v in r.hgetall(key).items():
                k2 = k.decode("utf-8") if isinstance(k, bytes) else k
                v2 = v.decode("utf-8") if isinstance(v, bytes) else v
                mapping[k2] = v2
            item["mapping"] = mapping
        else:
            # Cac kieu du lieu khac: luu bang coche DUMP de RESTORE duoc
            item["dump"] = r.dump(key).hex()
        items.append(item)

    path = out_dir / "redis_keys.json"
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  + redis_keys.json  ({len(items)} key)")
    return len(items)


def main():
    print("=" * 64)
    print("  BACKUP DU LIEU - De tai 06")
    print("=" * 64)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = EXPORT_DIR / f"backup_{stamp}"

    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[config.MONGO_DB_NAME]
    client.admin.command("ping")
    print(f"MongoDB   : {config.MONGO_URI} / {config.MONGO_DB_NAME}")

    r = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
    )
    r.ping()
    print(f"Redis     : {config.REDIS_HOST}:{config.REDIS_PORT} (db {config.REDIS_DB})")

    print("\n[1/2] Backup MongoDB:")
    mongo_result = backup_mongodb(db, out_dir)

    print("\n[2/2] Backup Redis:")
    redis_count = backup_redis(r, out_dir)

    # Luu them file RDB chuan cua Redis (khoi phuc bang cach copy vao thu muc data)
    try:
        r.save()
        print("  + Da tao dump.rdb (lenh SAVE) trong thu muc du lieu cua Redis")
    except Exception as exc:  # noqa: BLE001
        print(f"  [!] Khong tao duoc dump.rdb: {exc}")

    print("\nKet qua backup:")
    print(f"  Thu muc : {out_dir}")
    for name, count in mongo_result.items():
        print(f"  MongoDB collection '{name}': {count} document")
    print(f"  Redis   : {redis_count} key")
    print("\nKhoi phuc:  python data/restore.py " + str(out_dir))
    print("=" * 64)


if __name__ == "__main__":
    main()
