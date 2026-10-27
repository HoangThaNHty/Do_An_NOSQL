"""
services/article_service.py - NGHIEP VU BAI VIET

Noi dung nghiep vu (luon nghien dung cach truy van), va giao tiep voi
services/cache_service de dam bao CACHE INVALIDATION khi sua / xoa bai viet.

    Doc bai viet  -> cache_service.get_article(...)   (Cache-Aside)
    Sua bai viet  -> MongoDB update -> cache_service.invalidate_article(...)
    Xoa bai viet  -> MongoDB delete -> cache_service.invalidate_article(...)
"""

import time

from bson import ObjectId

from config import config
from models import article as article_model


class ArticleService:
    def __init__(self, db, cache_service):
        self.db = db
        self.cache = cache_service

    # ---------- Doc ----------
    def get_detail(self, article_id):
        """
        Doc chi tiet bai viet theo luu v Cache-Aside.
        :return: (article_dict, source)  source = 'cache' | 'database' | 'none'
        """
        data, source = self.cache.get_article(
            article_id,
            loader=lambda: self._load_from_database(article_id),
        )
        if data is None or data.get("status") != "published":
            return None, source
        article = article_model.to_dict(data)
        # So luot xem lay tu bo dem INCR tren Redis (khong doc tu MongoDB)
        article["views"] = self.cache.get_views(article_id)
        return article, source

    def _load_from_database(self, article_id):
        """
        Doc bai viet tu DB goc (MongoDB).
        Neu bat SIMULATED_DB_LATENCY_MS trong .env -> mo phong do tre mang
        (dung de demo khi MongoDB nam o may khac).
        """
        if config.SIMULATED_DB_LATENCY_MS > 0:
            time.sleep(config.SIMULATED_DB_LATENCY_MS / 1000)
        return article_model.get_article(self.db, article_id)

    def list_articles(self, page=1, per_page=9, category=None, keyword=None, sort="newest"):
        """
        Danh sach bai viet (co cache 60s cho danh sach).
        :return: (dict_ket_qua, source)
        """
        page, per_page = max(1, int(page)), min(100, max(1, int(per_page)))
        if sort == "views":
            return self.search(keyword, category, sort, page, per_page), "database"
        loader = lambda: self._build_list(page, per_page, category, keyword, sort)
        data, source = self.cache.get_article_list(
            page, sort, loader, category=category or "all", keyword=keyword or "", per_page=per_page
        )
        # Luot xem luon lay MOI tu bo dem INCR (du danh sach da duoc cache)
        self._enrich_views(data)
        return data, source

    def _enrich_views(self, result):
        """Gan luot xem moi nhat (doc tu Redis) vao danh sach bai viet."""
        if not result or not result.get("items"):
            return
        ids = [item.get("_id") for item in result["items"]]
        views = self.cache.get_views_many(ids)
        for item in result["items"]:
            item["views"] = views.get(str(item.get("_id")), 0)

    def _build_list(self, page, per_page, category, keyword, sort):
        result = article_model.list_articles(
            self.db,
            page=page,
            per_page=per_page,
            category=category,
            keyword=keyword,
            sort=sort,
        )
        items = []
        for doc in result["items"]:
            item = article_model.to_dict(doc)
            items.append(item)
        result["items"] = items
        self._enrich_views(result)
        return result

    def search(self, keyword, category=None, sort="newest", page=1, per_page=9, status="published"):
        """Tim kiem / loc / phan trang (chung mot ham, khong dung cache danh sach)."""
        counts = None
        if sort == "views":
            ids = [str(doc["_id"]) for doc in self.db["articles"].find({}, {"_id": 1})]
            counts = self.cache.get_views_many(ids)
        result = article_model.list_articles(
            self.db,
            page=page,
            per_page=per_page,
            category=category,
            keyword=keyword,
            sort=sort,
            status=status,
            view_counts=counts,
        )
        items = []
        for doc in result["items"]:
            item = article_model.to_dict(doc)
            items.append(item)
        result["items"] = items
        self._enrich_views(result)
        return result

    def increase_views(self, article_id):
        """Tang luot xem bang lenh INCR cua Redis."""
        return self.cache.incr_views(article_id)

    # ---------- Ghi (CRUD) ----------
    def create(self, data, author_id=None, author_name=""):
        """Them bai viet moi vao MongoDB va xoa cache danh sach."""
        self._validate(data)
        doc = article_model.create_article(
            self.db, data, author_id=author_id, author_name=author_name
        )
        self.cache.invalidate_lists()
        return article_model.to_dict(doc)

    def update(self, article_id, data):
        """
        Sua bai viet tren DB goc ROI xoa cache lien quan (CACHE INVALIDATION).
        """
        current = self.get(article_id)
        if not current:
            return None
        self._validate({**current, **data})
        updated = article_model.update_article(self.db, article_id, data)
        if updated:
            self.cache.invalidate_article(article_id)
        return article_model.to_dict(updated) if updated else None

    def delete(self, article_id):
        """Xoa bai viet va xoa cache lien quan."""
        ok = article_model.delete_article(self.db, article_id)
        if ok:
            self.cache.invalidate_article(article_id)
        return ok

    # ---------- Khac ----------
    def categories(self):
        cats = article_model.distinct_categories(self.db)
        return cats or article_model.CATEGORIES

    def popular(self, limit=5):
        """Bai viet duoc xem nhieu nhat (dung cho sidebar)."""
        return self.search("", sort="views", per_page=limit)["items"]

    def related(self, article, limit=3):
        docs = self.db["articles"].find({
            "status": "published", "category": article["category"],
            "_id": {"$ne": ObjectId(article["_id"])},
        }).sort("created_at", -1).limit(limit)
        result = {"items": [article_model.to_dict(doc) for doc in docs]}
        self._enrich_views(result)
        return result["items"]

    @staticmethod
    def _validate(data):
        for field, label in (("title", "tiêu đề"), ("content", "nội dung")):
            if not isinstance(data.get(field), str) or not data[field].strip():
                raise ValueError(f"Vui lòng nhập {label} bài viết.")
        if data.get("status", "published") not in ("published", "draft"):
            raise ValueError("Trạng thái bài viết không hợp lệ.")
        if data.get("category", article_model.CATEGORIES[0]) not in article_model.CATEGORIES:
            raise ValueError("Chuyên mục không hợp lệ.")
        if not isinstance(data.get("tags", []), list):
            raise ValueError("Thẻ bài viết phải là một danh sách.")

    def total(self):
        return article_model.count_articles(self.db)

    def get(self, article_id):
        doc = article_model.get_article(self.db, article_id)
        return article_model.to_dict(doc) if doc else None
