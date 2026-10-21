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
    """Decorator: yeu cau quyen admin hoac editor."""

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
