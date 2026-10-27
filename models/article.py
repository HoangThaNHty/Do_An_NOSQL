"""
models/article.py - MODEL cho collection `articles` trong MongoDB (DB goc)

Trach nhiemm:
    - Tao index (slug unique, category+created_at, author, created_at)
    - CRUD co ban tren DB goc
    - Truy van co ban: lay danh sach, chi tiet
    - Truy van nang cao: tim kiem (keyword), loc (category), sap xep, phan trang
"""

from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, TEXT
from models.search import relevance

CATEGORIES = [
    "Công nghệ",
    "Kinh tế",
    "Thể thao",
    "Khoa học",
    "Xã hội",
    "Đời sống",
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
    """
    Chuyen ObjectId -> str va datetime -> chuoi de hien thi/JSON hoa.
    Xu ly ca 2 truong hop: gia tri datetime tu MongoDB va chuoi ISO da
    serialize (truong hop doc tu Redis Cache).
    """
    if not doc:
        return None
    out = dict(doc)
    out["_id"] = str(doc["_id"])
    if isinstance(out.get("author"), ObjectId):
        out["author"] = str(out["author"])
    for key in ("created_at", "updated_at"):
        value = out.get(key)
        if isinstance(value, datetime):
            out[key] = value.strftime("%d/%m/%Y %H:%M")
        elif isinstance(value, str) and value:
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                out[key] = parsed.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                pass
    return out


def slugify(text):
    """Tao slug don gian cho tieu de."""
    import re
    import unicodedata

    text = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text) or "bai-viet"


# ------------------------------------------------------------------
# Truy van co ban
# ------------------------------------------------------------------
def get_article(db, article_id):
    """Lay 1 bài viết theo id. Tra None neu không tồn tại / id khong hop le."""
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
    view_counts=None,
):
    """
    Truy van danh sach bài viết co phan trang + loc + tim kiem + sap xep.

    day   : dieu kien loc
    sort  : 'newest' | 'oldest' | 'views' | 'title'
    """
    page = max(1, int(page))
    per_page = min(100, max(1, int(per_page)))
    query = {}
    if status:
        query["status"] = status
    if category and category != "all":
        query["category"] = category
    sort_spec = SORT_OPTIONS.get(sort, SORT_OPTIONS["newest"])
    if keyword:
        candidates = list(db["articles"].find(query).sort(sort_spec))
        scored = [(doc, relevance(doc, keyword)) for doc in candidates]
        ranked = [(doc, score) for doc, score in scored if score > 0]
        if sort == "relevance":
            ranked.sort(key=lambda pair: pair[1], reverse=True)
        if sort == "views" and view_counts is not None:
            ranked.sort(key=lambda pair: view_counts.get(str(pair[0]["_id"]), 0), reverse=True)
        total = len(ranked)
        items = [doc for doc, _ in ranked[(page - 1) * per_page:page * per_page]]
    elif sort == "views" and view_counts is not None:
        total = db["articles"].count_documents(query)
        ranked = list(db["articles"].find(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]))
        ranked.sort(key=lambda doc: view_counts.get(str(doc["_id"]), 0), reverse=True)
        items = ranked[(page - 1) * per_page:page * per_page]
    else:
        total = db["articles"].count_documents(query)
        items = list(
            db["articles"]
            .find(query)
            .sort(sort_spec)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )
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
        "image_alt": data.get("image_alt", "").strip(),
        "image_caption": data.get("image_caption", "").strip(),
        "seed_version": data.get("seed_version"),
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
    for key in ("title", "summary", "content", "image", "image_alt", "image_caption", "category", "status"):
        if key in data and data[key] is not None:
            fields[key] = data[key]
    if "tags" in data and data["tags"] is not None:
        fields["tags"] = data["tags"]
    current = get_article(db, article_id)
    if current and "image" in fields and fields["image"] != current.get("image"):
        # A changed photo must not keep a caption describing the previous photo.
        fields.setdefault("image_alt", "")
        fields.setdefault("image_caption", "")
    if "title" in fields:
        base = slugify(fields["title"])
        slug, suffix = base, 1
        while db["articles"].find_one({"slug": slug, "_id": {"$ne": ObjectId(article_id)}}):
            suffix += 1
            slug = f"{base}-{suffix}"
        fields["slug"] = slug
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
