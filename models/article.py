"""
models/article.py - MODEL cho collection `articles` trong MongoDB (DB goc)

Trach nhiemm:
    - Tao index (slug unique, title text, category+created_at, author)
    - CRUD co ban tren DB goc
    - Truy van co ban: lay danh sach, chi tiet
    - Truy van nang cao: tim kiem (keyword), loc (category), sap xep, phan trang
"""

from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, TEXT

CATEGORIES = [
    "Cong nghe",
    "Kinh te",
    "The thao",
    "Khoa hoc",
    "Xa hoi",
    "Doi song",
]

SORT_OPTIONS = {
    "newest": [("created_at", DESCENDING)],
    "oldest": [("created_at", ASCENDING)],
    "views": [("views", DESCENDING)],
    "title": [("title", ASCENDING)],
}


def utcnow():
    return datetime.now(timezone.utc)


def ensure_indexes(db):
    """Tao index cho collection articles."""
    articles = db["articles"]
    articles.create_index([("slug", ASCENDING)], unique=True, name="idx_articles_slug")
    articles.create_index(
        [("category", ASCENDING), ("created_at", DESCENDING)],
        name="idx_articles_category_created",
    )
    articles.create_index([("author", ASCENDING)], name="idx_articles_author")
    articles.create_index([("created_at", DESCENDING)], name="idx_articles_created")
    return articles


# ------------------------------------------------------------------
# Chuyen doi du lieu
# ------------------------------------------------------------------
def to_dict(doc):
    """Chuyen ObjectId -> str va datetime -> chuoi de hien thi/JSON hoa."""
    if not doc:
        return None
    out = dict(doc)
    out["_id"] = str(doc["_id"])
    for key in ("created_at", "updated_at"):
        if isinstance(out.get(key), datetime):
            out[key] = out[key].strftime("%d/%m/%Y %H:%M")
    return out


def slugify(text):
    """Tao slug don gian cho tieu de."""
    import re
    import unicodedata

    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text) or "bai-viet"


# ------------------------------------------------------------------
# Truy van co ban
# ------------------------------------------------------------------
def get_article(db, article_id):
    """Lay 1 bai viet theo id. Tra None neu khong ton tai / id khong hop le."""
    if not ObjectId.is_valid(article_id):
        return None
    return db["articles"].find_one({"_id": ObjectId(article_id)})


def list_articles(
    db,
    page=1,
    per_page=9,
    category=None,
    keyword=None,
    sort="newest",
    status="published",
):
    """
    Truy van danh sach bai viet co phan trang + loc + tim kiem + sap xep.

    day   : dieu kien loc
    sort  : 'newest' | 'oldest' | 'views' | 'title'
    """
    page = max(1, int(page))
    per_page = max(1, int(per_page))
    query = {}
    if status:
        query["status"] = status
    if category and category != "all":
        query["category"] = category
    if keyword:
        # Tim kiem "tuong doi" - dung regex de phong bi loi dac biet regex
        import re

        pattern = re.escape(keyword)
        query["$or"] = [
            {"title": {"$regex": pattern, "$options": "i"}},
            {"summary": {"$regex": pattern, "$options": "i"}},
            {"content": {"$regex": pattern, "$options": "i"}},
            {"tags": {"$regex": pattern, "$options": "i"}},
        ]

    sort_spec = SORT_OPTIONS.get(sort, SORT_OPTIONS["newest"])
    total = db["articles"].count_documents(query)
    cursor = (
        db["articles"]
        .find(query)
        .sort(sort_spec)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    items = list(cursor)
    total_pages = max(1, (total + per_page - 1) // per_page)
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }


# ------------------------------------------------------------------
# CRUD (chinh MongoDB - DB goc)
# ------------------------------------------------------------------
def create_article(db, data, author_id=None, author_name=""):
    now = utcnow()
    title = data.get("title", "").strip()
    doc = {
        "title": title,
        "slug": slugify(title),
        "summary": data.get("summary", "").strip(),
        "content": data.get("content", "").strip(),
        "image": data.get("image", "").strip(),
        "category": data.get("category", CATEGORIES[0]),
        "tags": data.get("tags", []),
        "status": data.get("status", "published"),
        "author": ObjectId(author_id) if author_id else None,
        "author_name": author_name,
        "views": 0,
        "created_at": now,
        "updated_at": now,
    }
    # Dam bao slug duy nhat
    base = doc["slug"]
    i = 1
    while db["articles"].find_one({"slug": doc["slug"]}):
        i += 1
        doc["slug"] = f"{base}-{i}"
    result = db["articles"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def update_article(db, article_id, data):
    if not ObjectId.is_valid(article_id):
        return None
    fields = {}
    for key in ("title", "summary", "content", "image", "category", "status"):
        if key in data and data[key] is not None:
            fields[key] = data[key]
    if "tags" in data and data["tags"] is not None:
        fields["tags"] = data["tags"]
    if "title" in fields:
        fields["slug"] = slugify(fields["title"])
    fields["updated_at"] = utcnow()
    db["articles"].update_one({"_id": ObjectId(article_id)}, {"$set": fields})
    return get_article(db, article_id)


def delete_article(db, article_id):
    if not ObjectId.is_valid(article_id):
        return False
    result = db["articles"].delete_one({"_id": ObjectId(article_id)})
    return result.deleted_count > 0


def distinct_categories(db):
    return sorted(db["articles"].distinct("category"))


def count_articles(db):
    return db["articles"].count_documents({})
