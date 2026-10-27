"""Các thao tác luôn lấy chủ danh sách từ phiên đăng nhập, không từ client."""
from flask import Blueprint, current_app, g, jsonify, render_template, request

from controllers import login_required

saved_bp = Blueprint("saved", __name__)


def service():
    return current_app.extensions["saved_service"]


@saved_bp.get("/saved")
@login_required
def index():
    result = service().list(g.current_user["user_id"], request.args.get("page", 1, type=int))
    return render_template("saved_articles.html", result=result)


@saved_bp.get("/api/saved")
@login_required
def api_list():
    result = service().list(g.current_user["user_id"], request.args.get("page", 1, type=int),
                            request.args.get("per_page", 9, type=int))
    return jsonify(success=True, data=result)


@saved_bp.route("/api/saved/<article_id>", methods=["PUT", "DELETE"])
@login_required
def api_change(article_id):
    if request.headers.get("Origin") and request.headers["Origin"] != request.host_url.rstrip("/"):
        return jsonify(success=False, error="Nguồn yêu cầu không hợp lệ."), 403
    user_id = g.current_user["user_id"]
    if request.method == "PUT":
        if not service().save(user_id, article_id):
            return jsonify(success=False, error="Không tìm thấy bài viết đã xuất bản."), 404
    else:
        service().remove(user_id, article_id)
    return jsonify(success=True, saved=request.method == "PUT")
