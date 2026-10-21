"""
services/cache_service.py - TANG NGHIEP VU CACHE-ASPIDE  (trung tam cua De tai 06)

================================================================================
NGUYEN LY CACHE-ASPIDE (bai giang cho GV)
================================================================================
Application luon doc tu Redis TRUOC. Redis chi la "bo dem" (cache), khong phai
noi luu du lieu chinh - du lieu chinh van nam trong MongoDB.

    Doc bai viet:
        1) GET article:cache:<id> tren Redis
             |- HIT  -> tra ket qua ngay tu Redis (khong cham MongoDB)   <5ms
             `- MISS -> doc MongoDB -> ghi nguoc lai Redis kem TTL -> tra ve

    Sua / xoa bai viet:
        -> XOA ngay key article:cache:<id> (Cache Invalidation)
        -> Lan doc sau se la Cache Miss va lay du lieu moi tu MongoDB.

================================================================================
DUONG DAN KEY (quy uoc chung cho ca nhom)
================================================================================
    article:cache:<id>       Hash   Noi dung bai viet da cache      TTL 300s
    article:cache:hot:<id>   Hash   Bai "nong" giu cache lau hon   TTL 1800s
    article:list:<p>:<sort>  String JSON  Danh sach bai viet      TTL 60s
    article:views:<id>       String (counter)  Luot xem (INCR)    TTL 86400s
    stats:cache:hits         String (counter)  So lan Cache Hit
    stats:cache:misses       String (counter)  So lan Cache Miss
"""

import json

import redis


class CacheService:
    """
    Lop dich vu cache. Duoc khoi tao 1 lan (singleton) trong app.py va
    gan vao app.extensions de cac controller / service dung chung.
    """

    # ---------- He so dem Hit/Miss (phuc vu demo) ----------
    KEY_HITS = "stats:cache:hits"
    KEY_MISSES = "stats:cache:misses"

    def __init__(self, redis_client: redis.Redis, config):
        self.redis = redis_client
        self.config = config
        self.ttl_article = config.TTL_ARTICLE_CACHE
        self.ttl_article_hot = config.TTL_ARTICLE_CACHE_HOT
        self.ttl_list = config.TTL_ARTICLE_LIST
        self.ttl_views = config.TTL_VIEWS

    # ==================================================================
    # 1. CAC KEY
    # ==================================================================
    @staticmethod
    def article_key(article_id):
        """Key cache noi dung bai viet."""
        return f"article:cache:{article_id}"

    @staticmethod
    def article_hot_key(article_id):
        """Key cache bai 'nong' (TTL dai hon)."""
        return f"article:cache:hot:{article_id}"

    @staticmethod
    def views_key(article_id):
        """Key bo dem luot xem - tang bang lenh INCR."""
        return f"article:views:{article_id}"

    @staticmethod
    def list_key(page, sort, category="all", keyword=""):
        """Key cache danh sach bai viet."""
        tag = f"{category}-{keyword or 'all'}".replace(" ", "_")
        return f"article:list:{page}:{sort}:{tag}"

    # ==================================================================
    # 2. DOC / GHI BAI VIET - TRIEN KHAI CACHE-ASPIDE
    # ==================================================================
    def get_article(self, article_id, loader, hot=False):
        """
        Doc 1 bai viet theo luu v Cache-Aside.

        :param article_id: id cua bai viet
        :param loader:    ham callback se duoc goi KHI CACHE MISS de lay du lieu
                          tu DB goc (vi du: lambda: models.article.get_article(db, id))
        :param hot:       True -> dung key/TTL cho bai 'nong'
        :return: (data, source)  source = 'cache' | 'database' | 'none'
        """
        key = self.article_hot_key(article_id) if hot else self.article_key(article_id)
        ttl = self.ttl_article_hot if hot else self.ttl_article

        # --- BUOC 1: kiem tra Redis (Cache HIT?) ---
        cached = self.redis.hgetall(key)
        if cached:
            self.redis.incr(self.KEY_HITS)
            return self._decode_hash(cached), "cache"

        # --- BUOC 2: Cache MISS -> doc DB goc ---
        self.redis.incr(self.KEY_MISSES)
        data = loader()
        if not data:
            return None, "none"

        # --- BUOC 3: ghi nguoc lai Redis kem TTL (EXPIRE) ---
        self.set_article(article_id, data, ttl=ttl, hot=hot)
        return data, "database"

    def set_article(self, article_id, data, ttl=None, hot=False):
        """Ghi bai viet vao Redis (HSET) va dat TTL (EXPIRE)."""
        if not data:
            return False
        key = self.article_hot_key(article_id) if hot else self.article_key(article_id)
        ttl = ttl or (self.ttl_article_hot if hot else self.ttl_article)

        mapping = {
            "_id": str(data.get("_id", article_id)),
            "title": str(data.get("title", "")),
            "summary": str(data.get("summary", "")),
            "content": str(data.get("content", "")),
            "image": str(data.get("image", "")),
            "category": str(data.get("category", "")),
            "tags": json.dumps(data.get("tags", []), ensure_ascii=False),
            "author_name": str(data.get("author_name", "")),
            "status": str(data.get("status", "published")),
            "created_at": str(data.get("created_at", "")),
            "updated_at": str(data.get("updated_at", "")),
        }
        pipe = self.redis.pipeline()
        pipe.hset(key, mapping=mapping)
        pipe.expire(key, ttl)
        pipe.execute()
        return True

    def invalidate_article(self, article_id):
        """
        CACHE INVALIDATION - goi khi bai viet bi SUA hoac XOA.
        Xoa sach key lien quan de lan sau doc se thay du lieu moi tu DB goc.
        """
        removed = 0
        for key in (self.article_key(article_id), self.article_hot_key(article_id)):
            if self.redis.exists(key):
                removed += self.redis.delete(key)
        # Xoa luu cache danh sach (vi danh sach chua tieu de cu)
        for key in self.redis.keys("article:list:*"):
            self.redis.delete(key)
        return removed

    # ==================================================================
    # 3. BO DEM LUOT XEM - LENH INCR
    # ==================================================================
    def incr_views(self, article_id, ttl=None):
        """
        Tang luot xem bang lenh INCR (atomic, an toan khi nhieu nguoi dung
        truy cap cung luc). Dung SET NX de tranh dem trung khi F5 lien tuc.
        """
        key = self.views_key(article_id)
        ttl = ttl or self.ttl_views
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl)
        views, _ = pipe.execute()
        return int(views)

    def get_views(self, article_id):
        """Doc so luot xem hien tai (0 neu chua co)."""
        value = self.redis.get(self.views_key(article_id))
        return int(value) if value else 0

    def get_views_many(self, article_ids):
        """
        Doc nhieu bo dem luot xem trong 1 lan round-trip (pipeline).
        Dung khi hien thi danh sach bai viet de luot xem luon moi nhat.
        """
        ids = [str(i) for i in article_ids if i]
        if not ids:
            return {}
        pipe = self.redis.pipeline()
        for article_id in ids:
            pipe.get(self.views_key(article_id))
        values = pipe.execute()
        return {
            article_id: int(value) if value else 0
            for article_id, value in zip(ids, values)
        }

    # ==================================================================
    # 4. CACHE DANH SACH BAI VIET
    # ==================================================================
    def get_article_list(self, page, sort, loader, category="all", keyword=""):
        """Cache danh sach bai viet theo trang/sap xep/loc/tim kiem."""
        key = self.list_key(page, sort, category, keyword)
        cached = self.redis.get(key)
        if cached:
            self.redis.incr(self.KEY_HITS)
            return json.loads(cached), "cache"
        self.redis.incr(self.KEY_MISSES)
        data = loader()
        payload = json.dumps(data, default=str, ensure_ascii=False)
        self.redis.set(key, payload, ex=self.ttl_list)
        return data, "database"

    def invalidate_lists(self):
        """Xoa toan bo cache danh sach."""
        keys = self.redis.keys("article:list:*")
        if keys:
            return self.redis.delete(*keys)
        return 0

    # ==================================================================
    # 5. THONG KE (phuc vu demo)
    # ==================================================================
    def get_stats(self):
        """Lay so lieu Hit/Miss va so key dang co tren Redis."""
        hits = self.redis.get(self.KEY_HITS)
        misses = self.redis.get(self.KEY_MISSES)
        total_keys = self.redis.dbsize()
        return {
            "hits": int(hits) if hits else 0,
            "misses": int(misses) if misses else 0,
            "total_keys": total_keys,
            "dbsize": self.redis.info("memory").get("used_memory_human"),
        }

    def reset_stats(self):
        self.redis.delete(self.KEY_HITS, self.KEY_MISSES)

    def ttl_of(self, key):
        """Tra ve TTL con lai cua 1 key (giay). -1 = khong co TTL, -2 = khong ton tai."""
        return self.redis.ttl(key)

    # ==================================================================
    # TIEN ICH
    # ==================================================================
    @staticmethod
    def _decode_hash(cached):
        """Chuyen du lieu tu Redis Hash (bytes) ve dict kieu Python."""
        out = {}
        for k, v in cached.items():
            key = k.decode("utf-8") if isinstance(k, bytes) else k
            val = v.decode("utf-8") if isinstance(v, bytes) else v
            if key == "tags":
                try:
                    val = json.loads(val)
                except (TypeError, ValueError):
                    val = []
            out[key] = val
        return out
