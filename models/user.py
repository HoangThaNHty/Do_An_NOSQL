"""
models/user.py - MODEL cho collection `users` trong MongoDB (DB goc)

Trach nhiemm:
    - Tao index (email unique, username unique)
    - Tao user moi (hash mat khau bang werkzeug - KHONG luu mat khau goc)
    - Tim user theo email / username
    - Kiem tra mat khau
"""

from datetime import datetime, timezone

from pymongo import ASCENDING
from werkzeug.security import check_password_hash, generate_password_hash


def utcnow():
    """Thoi gian UTC hien tai (chu y khi luu vao MongoDB)."""
    return datetime.now(timezone.utc)


def ensure_indexes(db):
    """Tao index cho collection users (goi 1 lan khi khoi dong app)."""
    users = db["users"]
    users.create_index([("email", ASCENDING)], unique=True, name="idx_users_email")
    users.create_index([("username", ASCENDING)], unique=True, name="idx_users_username")
    users.create_index([("role", ASCENDING)], name="idx_users_role")
    return users


def create_user(db, username, email, password, full_name="", role="reader"):
    """Tao user moi. Mat khau duoc hash bang scrypt (werkzeug.security)."""
    now = utcnow()
    doc = {
        "username": username,
        "email": email,
        "password_hash": generate_password_hash(password),
        "full_name": full_name,
        "role": role,
        "avatar": None,
        "created_at": now,
        "last_login": None,
    }
    result = db["users"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def find_by_email(db, email):
    return db["users"].find_one({"email": email})


def find_by_username(db, username):
    return db["users"].find_one({"username": username})


def find_by_id(db, user_id):
    from bson import ObjectId

    if not ObjectId.is_valid(user_id):
        return None
    return db["users"].find_one({"_id": ObjectId(user_id)})


def verify_password(user, password):
    """Kiem tra mat khau. user co the None."""
    if not user or "password_hash" not in user:
        return False
    return check_password_hash(user["password_hash"], password)


def update_last_login(db, user_id):
    db["users"].update_one(
        {"_id": user_id},
        {"$set": {"last_login": utcnow()}},
    )


def list_users(db):
    users = list(db["users"].find().sort("created_at", -1))
    for u in users:
        u.pop("password_hash", None)
    return users


def public_user(user):
    """Loai bo truong nhay cam khi gui ra giao dien / JSON."""
    if not user:
        return None
    return {
        "id": str(user.get("_id")),
        "username": user.get("username"),
        "email": user.get("email"),
        "full_name": user.get("full_name"),
        "role": user.get("role"),
        "created_at": user.get("created_at"),
        "last_login": user.get("last_login"),
    }
