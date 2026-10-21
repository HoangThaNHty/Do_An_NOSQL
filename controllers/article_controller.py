"""
controllers/article_controller.py - CONTROLLER BAI VIET

Phan biet 2 loai route trong cung 1 controller:
  - Route giao dien (HTML) : /, /articles, /articles/<id>
  - Route API (JSON)       : /api/articles...
"""

from flask import Blueprint, current_app, jsonify, render_template, request

from controllers import login_required

article_bp = Blueprint("article", __name__)


def _services():
    return (
        current_app.extensions["article_service"],
        current_app.extensions["cache_service"],
    )


# ======================================================================
# PHẦN GIAO DIỆN (VIEW)
# ======================================================================
@article_bp.get("/")
def index():
    """
    Trang chu - khoi HERO (1 bai noi bat + 4 bai phu) va cac block theo chuyen muc.
    Du lieu lay 1 lan tu DB (30 bai moi nhat) roi nhom theo chuyen muc.
    """
    article_service, _ = _services()
    result, source = article_service.list_articles(page=1, per_page=30, sort="newest")
    items = result["items"]

    featured = items[0] if items else None
    side_items = items[1:5]

    # Nhom bai viet theo chuyen muc (bo 5 bai da len hero)
    sections = []
    for category in article_service.categories():
        group = [a for a in items if a.get("category") == category]
        if len(group) >= 3:
            sections.append({"category": category, "articles": group[:4]})

    return render_template(
        "index.html",
        articles=items,
        featured=featured,
        side_items=side_items,
        sections=sections,
        source=source,
        categories=article_service.categories(),
        active_category="all",
        keyword="",
        sort="newest",
    )


@article_bp.get("/articles")
def list_articles():
    """Danh sach bai viet + tim kiem + loc + phan trang + sap xep."""
    article_service, _ = _services()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 9, type=int)
    category = request.args.get("category", "all")
    keyword = request.args.get("q", "").strip()
    sort = request.args.get("sort", "newest")

    if keyword:
        result = article_service.search(
            keyword, category=category, sort=sort, page=page, per_page=per_page
        )
        source = "database"
    else:
        result, source = article_service.list_articles(
            page=page, per_page=per_page, category=category, sort=sort
        )

    return render_template(
        "articles.html",
        articles=result["items"],
        result=result,
        source=source,
        categories=article_service.categories(),
        active_category=category,
        keyword=keyword,
        sort=sort,
        popular=article_service.popular(5),
    )


@article_bp.get("/articles/<article_id>")
def article_detail(article_id):
    """
    Chi tiet bai viet - DOC THEO LUU V CACHE-ASPIDE.
    Lan 1: Cache MISS -> doc MongoDB -> ghi nguoc Redis kem TTL.
    Lan 2: Cache HIT  -> tra luon tu Redis.
    """
    article_service, _ = _services()
    article, source = article_service.get_detail(article_id)
    if not article:
        return render_template("404.html", title="Khong tim thay bai viet"), 404

    # Tang luot xem bang lenh INCR cua Redis
    article["views"] = article_service.increase_views(article_id)

    related, _ = article_service.list_articles(
        page=1, per_page=4, category=article.get("category")
    )
    return render_template(
        "article_detail.html",
        article=article,
        source=source,
        categories=article_service.categories(),
        related=[a for a in related["items"] if a["_id"] != article_id][:3],
    )


# ======================================================================
# PHẦN API (JSON)
# ======================================================================
@article_bp.get("/api/articles")
def api_list_articles():
    """GET /api/articles?page=&per_page=&category=&q=&sort="""
    article_service, _ = _services()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 9, type=int)
    category = request.args.get("category", "all")
    keyword = request.args.get("q", "").strip()
    sort = request.args.get("sort", "newest")

    if keyword:
        result = article_service.search(
            keyword, category=category, sort=sort, page=page, per_page=per_page
        )
    else:
        result, _ = article_service.list_articles(
            page=page, per_page=per_page, category=category, sort=sort
        )
    return jsonify({"success": True, "data": result})


@article_bp.get("/api/articles/search")
def api_search_articles():
    """GET /api/articles/search?q=&category=&sort=  (truy van nang cao)"""
    article_service, _ = _services()
    keyword = request.args.get("q", "").strip()
    result = article_service.search(
        keyword,
        category=request.args.get("category", "all"),
        sort=request.args.get("sort", "newest"),
        page=request.args.get("page", 1, type=int),
        per_page=request.args.get("per_page", 9, type=int),
    )
    return jsonify({"success": True, "data": result})


@article_bp.get("/api/articles/<article_id>")
def api_get_article(article_id):
    """GET /api/articles/<id> - doc qua Cache-Aside, kem chi danh nguon du lieu."""
    article_service, _ = _services()
    article, source = article_service.get_detail(article_id)
    if not article:
        return jsonify({"success": False, "error": "Khong tim thay bai viet"}), 404
    return jsonify({"success": True, "source": source, "data": article})


@article_bp.post("/api/articles")
@login_required
def api_create_article():
    """POST /api/articles - them bai viet moi vao MongoDB."""
    article_service, _ = _services()
    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload.get("title") or not payload.get("content"):
        return jsonify({"success": False, "error": "Thieu tieu de hoac noi dung"}), 400

    user = getattr(request, "user", None) or _current_user()
    article = article_service.create(
        payload,
        author_id=user.get("user_id") if user else None,
        author_name=user.get("full_name", "") if user else "",
    )
    return jsonify({"success": True, "data": article}), 201


@article_bp.put("/api/articles/<article_id>")
@login_required
def api_update_article(article_id):
    """
    PUT /api/articles/<id> - sua bai viet.
    Sau khi sua DB goc -> service tu dong XOA CACHE (Cache Invalidation).
    """
    article_service, _ = _services()
    payload = request.get_json(silent=True) or request.form.to_dict()
    article = article_service.update(article_id, payload)
    if not article:
        return jsonify({"success": False, "error": "Khong tim thay bai viet"}), 404
    return jsonify({"success": True, "data": article})


@article_bp.delete("/api/articles/<article_id>")
@login_required
def api_delete_article(article_id):
    """DELETE /api/articles/<id> - xoa bai viet + xoa cache lien quan."""
    article_service, _ = _services()
    ok = article_service.delete(article_id)
    if not ok:
        return jsonify({"success": False, "error": "Khong tim thay bai viet"}), 404
    return jsonify({"success": True, "message": "Da xoa bai viet va xoa cache lien quan"})


def _current_user():
    from flask import g

    return getattr(g, "current_user", None)
