"""
controllers/auth_controller.py - CONTROLLER DANG KY / DANG NHAP / DANG XUAT

Session luu trong Redis duoi dang Hash (services/session_service.py).
"""

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from controllers import login_required
from services.session_service import SessionService

auth_bp = Blueprint("auth", __name__)


def _session_service():
    return current_app.extensions["session_service"]


def _auth_service():
    return current_app.extensions["auth_service"]


def _make_session(user):
    """Tao session tren Redis va gan cookie trinh duyet."""
    session_service = _session_service()
    session_id = session_service.create_session(
        user,
        ip=request.headers.get("X-Forwarded-For", request.remote_addr),
        user_agent=request.headers.get("User-Agent", ""),
    )
    response = redirect(url_for("article.index"))
    response.set_cookie(
        SessionService.COOKIE_NAME,
        session_id,
        max_age=session_service.ttl,
        httponly=True,
        samesite="Lax",
    )
    return response


# ======================================================================
# GIAO DIEN
# ======================================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Trang dang nhap."""
    if getattr(g, "current_user", None):
        return redirect(url_for("article.index"))
    if request.method == "POST":
        identifier = request.form.get("identifier", "")
        password = request.form.get("password", "")
        user, error = _auth_service().authenticate(identifier, password)
        if error:
            flash(error, "danger")
            return render_template("login.html", identifier=identifier)
        response = _make_session(user)
        flash(f"Xin chao {user.get('full_name') or user.get('username')}!", "success")
        return response
    return render_template("login.html", identifier="")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Trang dang ky tai khoan moi."""
    if getattr(g, "current_user", None):
        return redirect(url_for("article.index"))
    if request.method == "POST":
        data = {
            "username": request.form.get("username", ""),
            "email": request.form.get("email", ""),
            "password": request.form.get("password", ""),
            "confirm_password": request.form.get("confirm_password", ""),
            "full_name": request.form.get("full_name", ""),
        }
        user, error = _auth_service().register(**data)
        if error:
            flash(error, "danger")
            return render_template("register.html", form=data)
        flash("Dang ky thanh cong. Hay dang nhap.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form={})


@auth_bp.get("/logout")
def logout():
    """Dang xuat - xoa key session tren Redis + xoa cookie."""
    session_service = _session_service()
    session_id = request.cookies.get(SessionService.COOKIE_NAME)
    if session_id:
        session_service.destroy_session(session_id)
    response = redirect(url_for("article.index"))
    response.delete_cookie(SessionService.COOKIE_NAME)
    flash("Ban da dang xuat. Phien tren Redis da duoc xoa.", "info")
    return response


@auth_bp.get("/profile")
@login_required
def profile():
    """Trang thong tin ca nhan + thong tin phien Redis hien tai."""
    session_service = _session_service()
    session_id = request.cookies.get(SessionService.COOKIE_NAME)
    session_data = session_service.get_session(session_id)
    ttl = session_service.get_ttl(session_id)
    return render_template(
        "profile.html",
        session_data=session_data,
        session_ttl=ttl,
        users=_auth_service().list_users() if g.current_user.get("role") == "admin" else [],
    )


# ======================================================================
# API
# ======================================================================
@auth_bp.post("/api/auth/register")
def api_register():
    """POST /api/auth/register"""
    payload = request.get_json(silent=True) or request.form.to_dict()
    user, error = _auth_service().register(
        username=payload.get("username", ""),
        email=payload.get("email", ""),
        password=payload.get("password", ""),
        confirm_password=payload.get("confirm_password", payload.get("password", "")),
        full_name=payload.get("full_name", ""),
    )
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True, "data": user}), 201


@auth_bp.post("/api/auth/login")
def api_login():
    """POST /api/auth/login - tra ve session_id de client tu luu cookie."""
    payload = request.get_json(silent=True) or request.form.to_dict()
    identifier = payload.get("identifier") or payload.get("email") or payload.get("username")
    user, error = _auth_service().authenticate(identifier, payload.get("password", ""))
    if error:
        return jsonify({"success": False, "error": error}), 401
    session_service = _session_service()
    session_id = session_service.create_session(
        user,
        ip=request.headers.get("X-Forwarded-For", request.remote_addr),
        user_agent=request.headers.get("User-Agent", ""),
    )
    response = jsonify(
        {
            "success": True,
            "data": {
                "user": user,
                "session_id": session_id,
                "session_key": session_service.session_key(session_id),
                "ttl": session_service.get_ttl(session_id),
            },
        }
    )
    # Gan cookie de client (Postman / trinh duyet) dung lai duoc phien
    response.set_cookie(
        SessionService.COOKIE_NAME,
        session_id,
        max_age=session_service.ttl,
        httponly=True,
        samesite="Lax",
    )
    return response


@auth_bp.get("/api/auth/session")
def api_session():
    """GET /api/auth/session - kiem tra phien hien tai (doc Hash tren Redis)."""
    session_service = _session_service()
    session_id = request.cookies.get(SessionService.COOKIE_NAME)
    session_data = session_service.get_session(session_id)
    if not session_data:
        return jsonify({"success": False, "error": "Khong co phien dang nhap"}), 401
    return jsonify(
        {
            "success": True,
            "data": session_data,
            "ttl": session_service.get_ttl(session_id),
        }
    )


@auth_bp.post("/api/auth/logout")
def api_logout():
    """POST /api/auth/logout - xoa session tren Redis."""
    session_service = _session_service()
    session_id = request.cookies.get(SessionService.COOKIE_NAME)
    destroyed = session_service.destroy_session(session_id)
    response = jsonify({"success": True, "destroyed": destroyed})
    response.delete_cookie(SessionService.COOKIE_NAME)
    return response
