"""Danh sách đọc sau: một Redis Set cho mỗi tài khoản, không đặt TTL."""
from bson import ObjectId

from models import article as article_model


class SavedService:
    def __init__(self, db, redis_client, article_service):
        self.db = db
        self.redis = redis_client
        self.articles = article_service

    @staticmethod
    def key(user_id):
        return f"user:saved:{user_id}"

    @staticmethod
    def article_id(value):
        if not ObjectId.is_valid(value):
            raise ValueError("Mã bài viết không hợp lệ.")
        return str(ObjectId(value))

    def contains(self, user_id, article_id):
        return bool(self.redis.sismember(self.key(user_id), self.article_id(article_id)))

    def save(self, user_id, article_id):
        article_id = self.article_id(article_id)
        if not self.db.articles.find_one({"_id": ObjectId(article_id), "status": "published"}, {"_id": 1}):
            return False
        self.redis.sadd(self.key(user_id), article_id)
        return True

    def remove(self, user_id, article_id):
        self.redis.srem(self.key(user_id), self.article_id(article_id))

    def list(self, user_id, page=1, per_page=9):
        page, per_page = max(1, page), min(100, max(1, per_page))
        members = self.redis.smembers(self.key(user_id))
        ids = [ObjectId(value.decode() if isinstance(value, bytes) else value)
               for value in members if ObjectId.is_valid(value.decode() if isinstance(value, bytes) else value)]
        query = {"_id": {"$in": ids}, "status": "published"}
        total = self.db.articles.count_documents(query)
        docs = self.db.articles.find(query).sort([("created_at", -1), ("_id", -1)]).skip((page - 1) * per_page).limit(per_page)
        result = {"items": [article_model.to_dict(doc) for doc in docs], "total": total,
                  "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page}
        self.articles._enrich_views(result)
        return result
