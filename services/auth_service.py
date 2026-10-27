"""
services/auth_service.py - NGHIEP VU DANG KY / DANG NHAP

- Mật khẩu luon duoc hash bang werkzeug.security (scrypt) truoc khi luu.
- Session KHONG luu o day; session_service se tao Hash tren Redis.
"""

import re

from pymongo.errors import DuplicateKeyError
from models import user as user_model


class AuthService:
    def __init__(self, db):
        self.db = db

    def register(self, username, email, password, confirm_password, full_name=""):
        """
        Đăng ký tai khoan moi.
        :return: (user_dict, error_message)
        """
        username = (username or "").strip()
        email = (email or "").strip().lower()
        full_name = (full_name or "").strip()

        if not username or not email or not password:
            return None, "Vui lòng điền đầy đủ tên đăng nhập, email và mật khẩu."
        if len(password) < 6:
            return None, "Mật khẩu phải có ít nhất 6 ký tự."
        if password != confirm_password:
            return None, "Hai lần nhập mật khẩu không khớp."
        if not re.fullmatch(r"[A-Za-z0-9_]{3,40}", username):
            return None, "Tên đăng nhập gồm 3–40 chữ cái không dấu, chữ số hoặc dấu gạch dưới."
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            return None, "Địa chỉ email không hợp lệ."
        if user_model.find_by_email(self.db, email):
            return None, "Email đã được sử dụng. Vui lòng dùng email khác."
        if user_model.find_by_username(self.db, username):
            return None, "Tên đăng nhập đã tồn tại."

        try:
            doc = user_model.create_user(
                self.db, username=username, email=email, password=password,
                full_name=full_name or username, role="reader",
            )
        except DuplicateKeyError:
            return None, "Email hoặc tên đăng nhập đã được sử dụng."
        return user_model.public_user(doc), None

    def authenticate(self, email_or_username, password):
        """
        Kiem tra thong tin dang nhap.
        :return: (user_dict, error_message)
        """
        identifier = (email_or_username or "").strip()
        if not identifier or not password:
            return None, "Vui lòng nhập email hoặc tên đăng nhập và mật khẩu."

        user = user_model.find_by_email(self.db, identifier.lower())
        if not user:
            user = user_model.find_by_username(self.db, identifier)
        if not user:
            return None, "Email, tên đăng nhập hoặc mật khẩu không đúng."
        if not user_model.verify_password(user, password):
            return None, "Email, tên đăng nhập hoặc mật khẩu không đúng."
        user_model.update_last_login(self.db, user["_id"])
        return user_model.public_user(user), None

    def get_user(self, user_id):
        user = user_model.find_by_id(self.db, user_id)
        return user_model.public_user(user) if user else None

    def list_users(self):
        return [user_model.public_user(u) for u in user_model.list_users(self.db)]
