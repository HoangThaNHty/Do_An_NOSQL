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
                return {"error": "Yeu cau dang nhap."}, 401
            flash("Ban can dang nhap de tiep tuc.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Decorator: yeu cau quyen admin hoac editor (quan tri noi dung)."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if not user:
            flash("Ban can dang nhap de tiep tuc.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if user.get("role") not in ("admin", "editor"):
            flash("Ban khong co quyen truy cap trang nay.", "danger")
            return redirect(url_for("article.index"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_only_required(view_func):
    """Decorator: CHI quyen 'admin' moi duoc (vd danh sach nguoi dung)."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if not user:
            flash("Ban can dang nhap de tiep tuc.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if user.get("role") != "admin":
            flash("Chi quan tri vien moi co quyen nay.", "danger")
            return redirect(url_for("admin.dashboard"))
        return view_func(*args, **kwargs)

    return wrapper


def editor_required(view_func):
    """
    Decorator cho API ghi du lieu (them/sua/xoa bai viet).
    Chi 'admin' va 'editor' duoc phep; 'reader' bi tu choi voi ma 403.
    Tra ve JSON 403 (khong phai redirect) vi dang goi qua API.
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if not user:
            return {"success": False, "error": "Yeu cau dang nhap."}, 401
        if user.get("role") not in ("admin", "editor"):
            return {
                "success": False,
                "error": "Tai khoan cua ban khong co quyen thao tac nay.",
                "role": user.get("role"),
            }, 403
        return view_func(*args, **kwargs)

    return wrapper
