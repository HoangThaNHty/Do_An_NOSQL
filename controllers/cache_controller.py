"""
controllers/cache_controller.py - CONTROLLER THEO DOI CACHE / SESSION (phuc vu demo)

Cac endpoint nay giup GV / nhom xem truc tiep trang thai Redis:
    GET  /api/cache/stats      -> so lan Lượt trúng bộ nhớ đệm / Miss, so key dang co
    GET  /api/cache/sessions   -> danh sach phien dang nhap + TTL con lai
    GET  /api/cache/keys       -> danh sach key Redis (dung cho tab Browser cua RedisInsight)
    POST /api/cache/reset      -> dat lai bo dem Hit/Miss
    POST /api/cache/invalidate -> xoa cache mot bài viết
"""

from flask import Blueprint, current_app, jsonify, request
from controllers import admin_api_required

cache_bp = Blueprint("cache", __name__, url_prefix="/api/cache")


def _cache():
    return current_app.extensions["cache_service"]


def _session_service():
    return current_app.extensions["session_service"]


@cache_bp.get("/stats")
@admin_api_required
def stats():
    """Thong ke Lượt trúng bộ nhớ đệm / Miss + so key dang luu tren Redis."""
    cache = _cache()
    redis_client = current_app.extensions["redis"]
    snapshot = cache.get_stats()
    server = redis_client.info("server")
    return jsonify(
        {
            "success": True,
            "data": {
                **snapshot,
                "hit_rate": (
                    round(
                        snapshot["hits"]
                        / max(1, snapshot["hits"] + snapshot["misses"])
                        * 100,
                        2,
                    )
                ),
                "uptime": server.get("uptime_in_seconds"),
                "redis_version": server.get("redis_version"),
            },
        }
    )


@cache_bp.get("/sessions")
@admin_api_required
def sessions():
    """Danh sach phien dang nhap (Hash tren Redis) kem TTL con lai."""
    session_service = _session_service()
    items = session_service.list_sessions()
    return jsonify(
        {
            "success": True,
            "count": len(items),
            "data": items,
        }
    )


@cache_bp.get("/keys")
@admin_api_required
def keys():
    """Danh sach key dang co tren Redis + TTL cua tung key."""
    redis_client = current_app.extensions["redis"]
    items = []
    for key in redis_client.keys("*"):
        key_str = key.decode("utf-8") if isinstance(key, bytes) else key
        items.append(
            {
                "key": key_str,
                "type": redis_client.type(key).decode("utf-8"),
                "ttl": redis_client.ttl(key),
            }
        )
    items.sort(key=lambda x: x["key"])
    return jsonify({"success": True, "count": len(items), "data": items})


@cache_bp.post("/reset")
@admin_api_required
def reset():
    """Dat lai bo dem Hit/Miss (dung khi bat dau buoi demo)."""
    _cache().reset_stats()
    return jsonify({"success": True, "message": "Đã đặt lại bộ đếm Hit/Miss"})


@cache_bp.post("/invalidate/<article_id>")
@admin_api_required
def invalidate(article_id):
    """Xoa cache cua 1 bài viết (dung cho buoc demo 'Lượt trượt bộ nhớ đệm' lan dau)."""
    removed = _cache().invalidate_article(article_id)
    return jsonify(
        {"success": True, "removed": removed, "article_id": article_id}
    )
