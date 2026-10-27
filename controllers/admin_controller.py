"""
controllers/admin_controller.py - CONTROLLER TRANG QUAN TRI

Trang /admin: quan tri bài viết (them - sua - xoa) va quan ly nguoi dung.
Moi thay doi deu di qua services/article_service de Cache Invalidation
duoc thuc hien tu dong.
"""

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for

from controllers import admin_only_required, admin_required, login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _services():
    return (
        current_app.extensions["article_service"],
        current_app.extensions["auth_service"],
    )


# ======================================================================
# DASHBOARD
# ======================================================================
@admin_bp.get("/")
@admin_required
def dashboard():
    """Trang chủ quan tri: thong ke nhanh."""
    article_service, auth_service = _services()
    cache = current_app.extensions["cache_service"]
    session_service = current_app.extensions["session_service"]
    stats = cache.get_stats()
    return render_template(
        "admin_dashboard.html",
        total_articles=article_service.total(),
        total_users=len(auth_service.list_users()),
        total_sessions=session_service.count_sessions(),
        cache_stats=stats,
        popular=article_service.popular(5),
        categories=article_service.categories(),
    )


@admin_bp.get("/cache")
@admin_required
def cache_dashboard():
    """
    Bảng điều khiển Bộ nhớ đệm & Phiên đăng nhập - noi trinh bay bang chung cho GV:
    so lan Lượt trúng bộ nhớ đệm/Miss, danh sach key Redis kem TTL, phien dang nhap.
    """
    cache = current_app.extensions["cache_service"]
    session_service = current_app.extensions["session_service"]
    redis_client = current_app.extensions["redis"]

    stats = cache.get_stats()
    total = stats["hits"] + stats["misses"]
    hit_rate = round(stats["hits"] / total * 100, 2) if total else 0.0

    keys = []
    for key in redis_client.keys("*"):
        key_str = key.decode("utf-8") if isinstance(key, bytes) else key
        keys.append(
            {
                "key": key_str,
                "type": redis_client.type(key).decode("utf-8"),
                "ttl": redis_client.ttl(key),
            }
        )
    keys.sort(key=lambda item: item["key"])

    return render_template(
        "admin_cache.html",
        cache_stats=stats,
        hit_rate=hit_rate,
        keys=keys,
        sessions=session_service.list_sessions(),
    )


# ======================================================================
# DANH SACH / THEM / SUA / XOA BAI VIET
# ======================================================================
@admin_bp.get("/articles")
@admin_required
def articles():
    """Danh sach bài viết trong trang quan tri + tim kiem + phan trang."""
    article_service, _ = _services()
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("q", "").strip()
    category = request.args.get("category", "all")
    result = article_service.search(keyword, category=category, page=page, per_page=10, status=None)
    return render_template(
        "admin_articles.html",
        articles=result["items"],
        result=result,
        categories=article_service.categories(),
        keyword=keyword,
        active_category=category,
    )


@admin_bp.route("/articles/create", methods=["GET", "POST"])
@admin_required
def create_article():
    """Thêm bài viết moi."""
    article_service, _ = _services()
    if request.method == "POST":
        payload = {
            "title": request.form.get("title", ""),
            "summary": request.form.get("summary", ""),
            "content": request.form.get("content", ""),
            "image": request.form.get("image", ""),
            "category": request.form.get("category", "Công nghệ"),
            "status": request.form.get("status", "published"),
            "tags": [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()],
        }
        if not payload["title"] or not payload["content"]:
            flash("Vui lòng nhập tiêu đề và nội dung.", "danger")
            return render_template(
                "admin_article_form.html", article=None, categories=article_service.categories()
            )
        try:
            article_service.create(payload, author_id=g.current_user.get("user_id"),
                                   author_name=g.current_user.get("full_name"))
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("admin_article_form.html", article=payload,
                                   is_edit=False, categories=article_service.categories()), 400
        flash("Đã thêm bài viết mới thành công.", "success")
        return redirect(url_for("admin.articles"))
    return render_template(
        "admin_article_form.html", article=None, categories=article_service.categories()
    )


@admin_bp.route("/articles/edit/<article_id>", methods=["GET", "POST"])
@admin_required
def edit_article(article_id):
    """Sửa bài viết. Luu -> xoa cache lien quan (Cache Invalidation)."""
    article_service, _ = _services()
    article = article_service.get(article_id)
    if not article:
        flash("Không tìm thấy bài viết.", "danger")
        return redirect(url_for("admin.articles"))

    if request.method == "POST":
        payload = {
            "title": request.form.get("title", ""),
            "summary": request.form.get("summary", ""),
            "content": request.form.get("content", ""),
            "image": request.form.get("image", ""),
            "category": request.form.get("category", "Công nghệ"),
            "status": request.form.get("status", "published"),
            "tags": [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()],
        }
        try:
            article_service.update(article_id, payload)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("admin_article_form.html", article={**article, **payload},
                                   categories=article_service.categories()), 400
        flash("Đã cập nhật bài viết và xóa bộ nhớ đệm cũ.", "success")
        return redirect(url_for("admin.articles"))

    return render_template(
        "admin_article_form.html", article=article, categories=article_service.categories()
    )


@admin_bp.post("/articles/delete/<article_id>")
@admin_required
def delete_article(article_id):
    """Xoa bài viết + xoa cache lien quan."""
    article_service, _ = _services()
    if article_service.delete(article_id):
        flash("Đã xóa bài viết và bộ nhớ đệm liên quan.", "success")
    else:
        flash("Xóa bài viết thất bại.", "danger")
    return redirect(url_for("admin.articles"))


# ======================================================================
# QUAN LY NGUOI DUNG
# ======================================================================
@admin_bp.get("/users")
@admin_only_required
def users():
    """Danh sách người dùng."""
    _, auth_service = _services()
    return render_template("admin_users.html", users=auth_service.list_users())
