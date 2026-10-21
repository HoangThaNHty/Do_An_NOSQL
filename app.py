"""
app.py - DIEM KHOI CHAY UNG DUNG (tuong duong Program.cs / Startup.cs cua ASP.NET Core)

App Factory Pattern:
    - Tao Flask app
    - Ket noi MongoDB (DB goc) + Redis (cache + session)
    - Khoi tao cac Service (tang nghiep vu)
    - Dang ky 4 Controller (Blueprint)
    - Middleware: nap current_user tu Session Redis moi request

Chay:   python app.py      ->  http://127.0.0.1:5000
"""

import redis
from flask import Flask, g, jsonify, render_template, request
from pymongo import MongoClient

from config import config
from controllers.admin_controller import admin_bp
from controllers.article_controller import article_bp
from controllers.auth_controller import auth_bp
from controllers.cache_controller import cache_bp
from models import article as article_model
from models import user as user_model
from services import ArticleService, AuthService, CacheService, SessionService


def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(config)

    # ------------------------------------------------------------------
    # 1. KET NOI MONGODB (DB goc)
    # ------------------------------------------------------------------
    mongo_client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=3000)
    db = mongo_client[config.MONGO_DB_NAME]
    app.extensions["mongo_client"] = mongo_client
    app.extensions["db"] = db

    # ------------------------------------------------------------------
    # 2. KET NOI REDIS (cache + session)
    # ------------------------------------------------------------------
    redis_client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
        socket_connect_timeout=3,
    )
    app.extensions["redis"] = redis_client

    # ------------------------------------------------------------------
    # 3. KHỞI TẠO TẦNG NGHIỆP VỤ (Dependency Injection)
    # ------------------------------------------------------------------
    cache_service = CacheService(redis_client, config)
    session_service = SessionService(redis_client, config)
    article_service = ArticleService(db, cache_service)
    auth_service = AuthService(db)

    app.extensions["cache_service"] = cache_service
    app.extensions["session_service"] = session_service
    app.extensions["article_service"] = article_service
    app.extensions["auth_service"] = auth_service

    # Tạo index MongoDB (đảm bảo truy vấn nâng cao chạy nhanh)
    with app.app_context():
        try:
            user_model.ensure_indexes(db)
            article_model.ensure_indexes(db)
        except Exception as exc:  # noqa: BLE001
            app.logger.warning("Khong tao duoc index: %s", exc)

    # ------------------------------------------------------------------
    # 4. ĐĂNG KÝ CONTROLLER
    # ------------------------------------------------------------------
    app.register_blueprint(article_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cache_bp)

    # ------------------------------------------------------------------
    # 5. MIDDLEWARE: nạp phiên đăng nhập từ Redis mỗi request
    # ------------------------------------------------------------------
    @app.before_request
    def load_current_user():
        """Đọc cookie session_id -> HGETALL session:<id> trên Redis -> g.current_user."""
        g.current_user = None
        g.session_id = None
        session_id = request.cookies.get(SessionService.COOKIE_NAME)
        if not session_id:
            return
        session_data = session_service.get_session(session_id)
        if session_data:
            g.current_user = session_data
            g.session_id = session_id
            # Gia han TTL (sliding expiration) khi user còn hoạt động
            session_service.refresh_session(session_id)

    @app.after_request
    def remove_expired_session_cookie(response):
        """Nếu cookie còn nhưng session đã hết hạn -> xóa cookie."""
        if request.cookies.get(SessionService.COOKIE_NAME) and not getattr(g, "current_user", None):
            response.delete_cookie(SessionService.COOKIE_NAME)
        return response

    @app.context_processor
    def inject_globals():
        """Biến dùng chung cho mọi template."""
        return {
            "current_user": getattr(g, "current_user", None),
            "site_name": config.SITE_NAME,
        }

    # ------------------------------------------------------------------
    # 6. HEALTH CHECK + ERROR HANDLER
    # ------------------------------------------------------------------
    @app.get("/api/health")
    def health():
        """Kiem tra ket noi MongoDB + Redis (dung de kiem thu nhanh)."""
        status = {"app": "ok", "mongo": "error", "redis": "error"}
        try:
            app.extensions["mongo_client"].admin.command("ping")
            status["mongo"] = "ok"
        except Exception as exc:  # noqa: BLE001
            status["mongo"] = str(exc)
        try:
            app.extensions["redis"].ping()
            status["redis"] = "ok"
        except Exception as exc:  # noqa: BLE001
            status["redis"] = str(exc)
        code = 200 if status["mongo"] == "ok" and status["redis"] == "ok" else 503
        return jsonify(status), code

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        app.logger.exception("Loi 500")
        return render_template("404.html", title="Loi may chu"), 500

    return app


app = create_app()


if __name__ == "__main__":
    print("=" * 60)
    print(f"  {config.SITE_NAME} - De tai 06: Cache-Aside + Session Management")
    print(f"  MongoDB : {config.MONGO_URI} / {config.MONGO_DB_NAME}")
    print(f"  Redis   : {config.REDIS_HOST}:{config.REDIS_PORT}")
    print(f"  URL     : http://127.0.0.1:{config.PORT}")
    print("=" * 60)
    app.run(host="127.0.0.1", port=config.PORT, debug=config.FLASK_DEBUG)
