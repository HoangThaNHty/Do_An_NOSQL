"""
services/auth_service.py - NGHIEP VU DANG KY / DANG NHAP

- Mat khau luon duoc hash bang werkzeug.security (scrypt) truoc khi luu.
- Session KHONG luu o day; session_service se tao Hash tren Redis.
"""

from models import user as user_model


class AuthService:
    def __init__(self, db):
        self.db = db

    def register(self, username, email, password, confirm_password, full_name=""):
        """
        Dang ky tai khoan moi.
        :return: (user_dict, error_message)
        """
        username = (username or "").strip()
        email = (email or "").strip().lower()
        full_name = (full_name or "").strip()

        if not username or not email or not password:
            return None, "Vui long dien day du ho ten, email va mat khau."
        if len(password) < 6:
            return None, "Mat khau phai co it nhat 6 ky tu."
        if password != confirm_password:
            return None, "Hai lan nhap mat khau khong khop."
        if user_model.find_by_email(self.db, email):
            return None, "Email da duoc su dung. Hay thong tin khac."
        if user_model.find_by_username(self.db, username):
            return None, "Ten dang nhap da ton tai."

        doc = user_model.create_user(
            self.db,
            username=username,
            email=email,
            password=password,
            full_name=full_name or username,
            role="editor",
        )
        return user_model.public_user(doc), None

    def authenticate(self, email_or_username, password):
        """
        Kiem tra thong tin dang nhap.
        :return: (user_dict, error_message)
        """
        identifier = (email_or_username or "").strip()
        if not identifier or not password:
            return None, "Vui long nhap email va mat khau."

        user = user_model.find_by_email(self.db, identifier.lower())
        if not user:
            user = user_model.find_by_username(self.db, identifier)
        if not user:
            return None, "Khong tim thay tai khoan."
        if not user_model.verify_password(user, password):
            return None, "Mat khau khong dung."
        user_model.update_last_login(self.db, user["_id"])
        return user_model.public_user(user), None

    def get_user(self, user_id):
        user = user_model.find_by_id(self.db, user_id)
        return user_model.public_user(user) if user else None

    def list_users(self):
        return [user_model.public_user(u) for u in user_model.list_users(self.db)]
