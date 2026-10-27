"""
controllers/__init__.py - TANG CONTROLLER

Controller trong Flask = Blueprint (Blueprint giup nhom route theo chuc nang).
O day tach cac decorator dung chung.
"""

from functools import wraps

from flask import flash, g, redirect, request, url_for


def login_required(view_func):
    """Decorator: chi cho phep truy cap khi da dang nhap (co session trong Redis)."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not getattr(g, "current_user", None):
            if request.path.startswith("/api/"):
                return {"error": "Yêu cầu đăng nhập."}, 401
            flash("Bạn cần đăng nhập để tiếp tục.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Decorator: yêu cầu quyền quản trị viên."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if not user:
            flash("Bạn cần đăng nhập để tiếp tục.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if user.get("role") != "admin":
            flash("Bạn không có quyền truy cập trang này.", "danger")
            return redirect(url_for("article.index"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_only_required(view_func):
    """Decorator: CHI quyen 'admin' moi duoc (vd danh sach nguoi dung)."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if not user:
            flash("Bạn cần đăng nhập để tiếp tục.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if user.get("role") != "admin":
            flash("Chỉ quản trị viên mới có quyền này.", "danger")
            return redirect(url_for("admin.dashboard"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_api_required(view_func):
    """
    Decorator cho API ghi du lieu (them/sua/xoa bài viết).
    Chỉ 'admin' được phép; 'reader' nhận mã 403.
    Tra ve JSON 403 (khong phai redirect) vi dang goi qua API.
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if not user:
            return {"success": False, "error": "Yêu cầu đăng nhập."}, 401
        if user.get("role") != "admin":
            return {
                "success": False,
                "error": "Tài khoản của bạn không có quyền thực hiện thao tác này.",
                "role": user.get("role"),
            }, 403
        return view_func(*args, **kwargs)

    return wrapper
