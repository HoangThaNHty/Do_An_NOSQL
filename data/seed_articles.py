"""Nạp 100 bài tiếng Việt có ảnh phù hợp và tài khoản dùng trong tài liệu demo."""
import argparse
import sys
from pathlib import Path
from pymongo import MongoClient
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import config
from models import article as article_model
from models import user as user_model
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TOTAL_ARTICLES = 100

DEMO_USERS = [
    ("admin", "admin@uit.edu.vn", "Quản trị viên", "admin"),
    ("reader", "reader@uit.edu.vn", "Độc giả", "reader"),
]
DEMO_PASSWORD = "123456"


def seed_users(db):
    """Tạo hai tài khoản mẫu; thông tin chỉ nằm trong tài liệu nội bộ."""
    created = []
    for username, email, full_name, role in DEMO_USERS:
        if user_model.find_by_email(db, email):
            print(f"  [skip] Tai khoan {username} da ton tai")
            continue
        user_model.create_user(
            db,
            username=username,
            email=email,
            password=DEMO_PASSWORD,
            full_name=full_name,
            role=role,
        )
        created.append(username)
    return created



def seed_articles(db, upload_dir: Path, reset=False):
    """Nạp bộ bài tiếng Việt với ảnh đã duyệt theo nội dung."""
    from data.article_catalog import build_catalog
    if reset:
        db["articles"].delete_many({})
    existing = db["articles"].count_documents({})
    if existing >= TOTAL_ARTICLES:
        return 0
    created = 0
    for data in build_catalog():
        if db["articles"].count_documents({}) >= TOTAL_ARTICLES:
            break
        if db["articles"].find_one({"title": data["title"]}):
            continue
        if not Path(__file__).resolve().parent.parent.joinpath(data["image"].lstrip("/")).exists():
            raise FileNotFoundError(data["image"])
        article_model.create_article(db, data, author_name="Ban biên tập")
        created += 1
    return created


def main():
    parser = argparse.ArgumentParser(description="Nap du lieu mau cho De tai 06")
    parser.add_argument("--reset", action="store_true", help="Xoa du lieu cu truoc khi nap")
    args = parser.parse_args()

    print("=" * 64)
    print("  SEED DU LIEU MAU - De tai 06 (Cache-Aside + Session Management)")
    print("=" * 64)

    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[config.MONGO_DB_NAME]
    client.admin.command("ping")
    print(f"MongoDB   : {config.MONGO_URI} / {config.MONGO_DB_NAME}")

    user_model.ensure_indexes(db)
    article_model.ensure_indexes(db)

    print("\n[1/3] Tai khoan demo:")
    for username in seed_users(db):
        print(f"  + {username} / {DEMO_PASSWORD}")

    print(f"\n[2/3] Bai viet + hinh anh (muc tieu {TOTAL_ARTICLES}):")
    created = seed_articles(db, config.IMAGES_FOLDER, reset=args.reset)
    print(f"  + Đã tạo {created} bài viết, dùng ảnh có sẵn trong {config.IMAGES_FOLDER}")

    print("\n[3/3] Kiem tra:")
    print(f"  Tong so bai viet : {db['articles'].count_documents({})}")
    print(f"  Tong so nguoi dung: {db['users'].count_documents({})}")
    print(f"  Chuyen muc       : {article_model.distinct_categories(db)}")
    print("\nHoan tat! Chay 'python app.py' de kiem tra tren trinh duyet.")
    print("=" * 64)


if __name__ == "__main__":
    main()
