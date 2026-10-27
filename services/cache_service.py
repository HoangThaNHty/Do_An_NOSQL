"""
services/cache_service.py - TANG NGHIEP VU CACHE-ASPIDE  (trung tam cua De tai 06)

================================================================================
NGUYEN LY CACHE-ASPIDE (bai giang cho GV)
================================================================================
Application luon doc tu Redis TRUOC. Redis chi la "bo dem" (cache), khong phai
noi luu du lieu chinh - du lieu chinh van nam trong MongoDB.

    Doc bai viet:
        1) HGETALL article:cache:<id> tren Redis
             |- HIT  -> tra ket qua ngay tu Redis (khong nap noi dung tu MongoDB)
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
import secrets
import time

import redis


class CacheBusyError(TimeoutError):
    """Hết thời gian chờ một yêu cầu khác nạp dữ liệu, có thể thử lại."""


class CacheService:
    """
    Lop dich vu cache. Duoc khoi tao 1 lan (singleton) trong app.py va
    gan vao app.extensions de cac controller / service dung chung.
    """

    # ---------- He so dem Hit/Miss (phuc vu demo) ----------
    KEY_HITS = "stats:cache:hits"
    KEY_MISSES = "stats:cache:misses"
    KEY_LOCK_WAITS = "stats:cache:lock_waits"
    KEY_LOCK_TIMEOUTS = "stats:cache:lock_timeouts"
    KEY_LIST_VERSION = "meta:article-list-version"
    RELEASE_LOCK = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('DEL', KEYS[1])
        end
        return 0
    """
    PUBLISH_CACHE = """
        if redis.call('GET', KEYS[1]) ~= ARGV[1] then return 0 end
        if ARGV[4] ~= '' and (redis.call('GET', KEYS[3]) or '0') ~= ARGV[4] then
            return 0
        end
        redis.call('DEL', KEYS[2])
        if ARGV[2] == 'hash' then
            redis.call('HSET', KEYS[2], unpack(ARGV, 5))
        else
            redis.call('SET', KEYS[2], ARGV[5])
        end
        redis.call('EXPIRE', KEYS[2], ARGV[3])
        redis.call('DEL', KEYS[1])
        return 1
    """

    def __init__(self, redis_client: redis.Redis, config):
        self.redis = redis_client
        self.config = config
        self.ttl_article = config.TTL_ARTICLE_CACHE
        self.ttl_article_hot = config.TTL_ARTICLE_CACHE_HOT
        self.ttl_list = config.TTL_ARTICLE_LIST
        self.ttl_views = config.TTL_VIEWS
        self.lock_ttl_ms = int(getattr(config, "CACHE_LOCK_TTL_MS", 10000))
        self.lock_wait_ms = int(getattr(config, "CACHE_LOCK_WAIT_MS", 2000))
        self.lock_poll_ms = int(getattr(config, "CACHE_LOCK_POLL_MS", 20))
        if min(self.lock_ttl_ms, self.lock_wait_ms, self.lock_poll_ms) <= 0:
            raise ValueError("Thời hạn khóa và thời gian chờ phải lớn hơn 0.")

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
    def lock_key(cache_key):
        return f"lock:{cache_key}"

    @staticmethod
    def views_key(article_id):
        """Key bo dem luot xem - tang bang lenh INCR."""
        return f"article:views:{article_id}"

    @staticmethod
    def list_key(page, sort, category="all", keyword="", per_page=9):
        """Key cache danh sach bai viet."""
        # JSON avoids collisions between filters; page size changes the result too.
        tag = json.dumps([category, keyword], ensure_ascii=False, separators=(",", ":"))
        return f"article:list:v2:{page}:{per_page}:{sort}:{tag}"

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

        def read():
            value = self.redis.hgetall(key)
            return self._decode_hash(value) if value else None
        return self._load_locked(key, read, loader, ttl, "hash")

    def _release_lock(self, key, token):
        return bool(self.redis.eval(self.RELEASE_LOCK, 1, key, token))

    def _load_locked(self, key, read, loader, ttl, kind, version_key=None):
        """SET NX PX: một chủ nạp; yêu cầu khác chờ có giới hạn, không đọc DB ồ ạt.

        Lua kiểm tra token ngay lúc ghi cache và lúc nhả khóa. Chủ đã hết lease
        không được ghi đè cache hay xóa khóa của chủ kế tiếp. Với danh sách,
        version ngăn ghi lại kết quả đã bị invalidate trong khi loader đang chạy.
        """
        lock_key = self.lock_key(key)
        deadline = time.monotonic() + self.lock_wait_ms / 1000
        waited = False
        while True:
            cached = read()
            if cached is not None:
                self.redis.incr(self.KEY_HITS)
                return cached, "cache"
            token = secrets.token_hex(24)
            if self.redis.set(lock_key, token, nx=True, px=self.lock_ttl_ms):
                published = False
                try:
                    # Another owner may have published between read() and SET NX.
                    cached = read()
                    if cached is not None:
                        self.redis.incr(self.KEY_HITS)
                        return cached, "cache"
                    version = (self.redis.get(version_key) or b"0") if version_key else ""
                    self.redis.incr(self.KEY_MISSES)
                    data = loader()
                    if data is None:
                        return None, "none"
                    if kind == "hash":
                        mapping = self._article_mapping(data.get("_id", ""), data)
                        payload = [part for pair in mapping.items() for part in pair]
                    else:
                        payload = [json.dumps(data, default=str, ensure_ascii=False)]
                    published = bool(self.redis.eval(
                        self.PUBLISH_CACHE, 3, lock_key, key, version_key or lock_key,
                        token, kind, ttl, version, *payload,
                    ))
                    return data, "database"
                finally:
                    if not published:
                        self._release_lock(lock_key, token)
            if not waited:
                self.redis.incr(self.KEY_LOCK_WAITS)
                waited = True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self.redis.incr(self.KEY_LOCK_TIMEOUTS)
                raise CacheBusyError("Nội dung đang được tải. Vui lòng thử lại sau ít giây.")
            time.sleep(min(self.lock_poll_ms / 1000, remaining))

    def set_article(self, article_id, data, ttl=None, hot=False):
        """Ghi bai viet vao Redis (HSET) va dat TTL (EXPIRE)."""
        if not data:
            return False
        key = self.article_hot_key(article_id) if hot else self.article_key(article_id)
        ttl = ttl or (self.ttl_article_hot if hot else self.ttl_article)

        mapping = self._article_mapping(article_id, data)
        pipe = self.redis.pipeline()
        pipe.hset(key, mapping=mapping)
        pipe.expire(key, ttl)
        pipe.execute()
        return True

    @staticmethod
    def _article_mapping(article_id, data):
        return {
            "_id": str(data.get("_id", article_id)),
            "slug": str(data.get("slug", "")),
            "author": json.dumps(str(data["author"]) if data.get("author") is not None else None),
            "seed_version": json.dumps(data.get("seed_version")),
            "title": str(data.get("title", "")),
            "summary": str(data.get("summary", "")),
            "content": str(data.get("content", "")),
            "image": str(data.get("image", "")),
            "image_alt": str(data.get("image_alt", "")),
            "image_caption": str(data.get("image_caption", "")),
            "category": str(data.get("category", "")),
            "tags": json.dumps(data.get("tags", []), ensure_ascii=False),
            "author_name": str(data.get("author_name", "")),
            "status": str(data.get("status", "published")),
            "created_at": str(data.get("created_at", "")),
            "updated_at": str(data.get("updated_at", "")),
        }

    def invalidate_article(self, article_id):
        """
        CACHE INVALIDATION - goi khi bai viet bi SUA hoac XOA.
        Xoa sach key lien quan de lan sau doc se thay du lieu moi tu DB goc.
        """
        keys = (self.article_key(article_id), self.article_hot_key(article_id))
        pipe = self.redis.pipeline()
        pipe.delete(*keys)
        # Revoke in-flight loaders; guarded publishing will refuse their old token.
        pipe.delete(*(self.lock_key(key) for key in keys))
        removed, _ = pipe.execute()
        self.invalidate_lists()
        return removed

    # ==================================================================
    # 3. BO DEM LUOT XEM - LENH INCR
    # ==================================================================
    def incr_views(self, article_id, ttl=None):
        """
        Tang luot xem bang lenh INCR (atomic, an toan khi nhieu nguoi dung
        truy cap cung luc). Mỗi lần tải trang HTML vẫn được tính một lượt xem.
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
    def get_article_list(self, page, sort, loader, category="all", keyword="", per_page=9):
        """Cache danh sach bai viet theo trang/sap xep/loc/tim kiem."""
        key = self.list_key(page, sort, category, keyword, per_page)
        def read():
            value = self.redis.get(key)
            return json.loads(value) if value is not None else None
        return self._load_locked(key, read, loader, self.ttl_list, "string", self.KEY_LIST_VERSION)

    def invalidate_lists(self):
        """Xoa toan bo cache danh sach."""
        self.redis.incr(self.KEY_LIST_VERSION)
        keys = list(self.redis.scan_iter("article:list:*"))
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
            "lock_waits": int(self.redis.get(self.KEY_LOCK_WAITS) or 0),
            "lock_timeouts": int(self.redis.get(self.KEY_LOCK_TIMEOUTS) or 0),
        }

    def reset_stats(self):
        self.redis.delete(self.KEY_HITS, self.KEY_MISSES, self.KEY_LOCK_WAITS, self.KEY_LOCK_TIMEOUTS)

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
            if key in ("tags", "author", "seed_version"):
                try:
                    val = json.loads(val)
                except (TypeError, ValueError):
                    val = [] if key == "tags" else None
            out[key] = val
        return out
