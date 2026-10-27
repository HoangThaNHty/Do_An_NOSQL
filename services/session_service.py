"""
services/session_service.py - QUAN LY PHIEN DANG NHAP LUU TREN REDIS (Hash)

================================================================================
YEU CAU CUA DE TAI
================================================================================
"Dung cau truc Hashes luu Session nguoi dung" + "Tu dong dem lui thoi gian
song (TTL)" -> moi Session duoc luu bang lenh HSET vao 1 key Hash:

    HSET session:<session_id> user_id <id>
                        username <ten>
                        email <email>
                        role <admin|reader>
                        login_at <timestamp>
                        ip <dia chi IP>
                        user_agent <trinh duyet>
    EXPIRE session:<session_id> 1800      <-- TTL 30 phut, tu dong dem lui

================================================================================
CO CHE LAM VIEC
================================================================================
    - Dang nhap   : tao SID ngau nhien (secrets.token_hex(32)) -> HSET -> EXPIRE -> gan cookie
    - Moi request : doc cookie -> EXISTS? -> HGETALL -> gan current_user
                    -> neu con thoi gian thi gia han TTL (refresh)
    - Het han     : Redis tu dong xoa key -> EXISTS = false -> nguoi dung
                    duoc chuyen ve trang dang nhap
    - Dang xuat   : DEL session:<sid> -> xoa cookie
"""

import secrets
from datetime import datetime, timezone


class SessionService:
    """Quan ly session luu tren Redis bang cau truc Hash."""

    COOKIE_NAME = "session_id"

    def __init__(self, redis_client, config):
        self.redis = redis_client
        self.config = config
        self.ttl = config.TTL_SESSION

    # ---------- Key ----------
    @staticmethod
    def session_key(session_id):
        return f"session:{session_id}"

    # ---------- Tao session moi ----------
    def create_session(self, user, ip=None, user_agent=None):
        """
        Tao phien dang nhap moi cho user va luu duoi dang Hash tren Redis.

        :return: session_id (chuoi hex 64 ky tu)
        """
        session_id = secrets.token_hex(32)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        key = self.session_key(session_id)

        mapping = {
            "session_id": session_id,
            "user_id": str(user.get("_id") or user.get("id", "")),
            "username": str(user.get("username", "")),
            "email": str(user.get("email", "")),
            "full_name": str(user.get("full_name", "")),
            "role": str(user.get("role", "reader")),
            "login_at": now,
            "ip": str(ip or ""),
            "user_agent": str(user_agent or ""),
        }
        pipe = self.redis.pipeline()
        pipe.hset(key, mapping=mapping)
        pipe.expire(key, self.ttl)
        pipe.execute()
        return session_id

    # ---------- Doc session ----------
    def get_session(self, session_id):
        """
        Doc thong tin phien tu Redis Hash.
        Tra None neu khong ton tai (het han hoac da dang xuat).
        """
        if not session_id:
            return None
        key = self.session_key(session_id)
        data = self.redis.hgetall(key)
        if not data:
            return None
        session = {}
        for k, v in data.items():
            key_name = k.decode("utf-8") if isinstance(k, bytes) else k
            val = v.decode("utf-8") if isinstance(v, bytes) else v
            session[key_name] = val
        return session

    # ---------- Gia han TTL (sliding expiration) ----------
    def refresh_session(self, session_id):
        """Gia han TTL khi user van dang hoat dong - tranh bi logout ngoai y mu."""
        if not session_id:
            return False
        key = self.session_key(session_id)
        if self.redis.exists(key):
            self.redis.expire(key, self.ttl)
            return True
        return False

    # ---------- Xoa session ----------
    def destroy_session(self, session_id):
        """Dang xuat: xoa hoan toan key Hash tren Redis."""
        if not session_id:
            return False
        return bool(self.redis.delete(self.session_key(session_id)))

    # ---------- Thong tin phien (demo) ----------
    def get_ttl(self, session_id):
        """TTL con lai cua phien (giay) - dung de chung minh TTL dem lui."""
        if not session_id:
            return -2
        return self.redis.ttl(self.session_key(session_id))

    def list_sessions(self):
        """
        Liet ke tat ca phien dang ton tai (dung cho trang demo / quản trị).
        Tra ve danh sach dict kem TTL con lai.
        """
        result = []
        for key in self.redis.keys("session:*"):
            data = self.redis.hgetall(key)
            if not data:
                continue
            item = {}
            for k, v in data.items():
                k2 = k.decode("utf-8") if isinstance(k, bytes) else k
                v2 = v.decode("utf-8") if isinstance(v, bytes) else v
                item[k2] = v2
            item["ttl"] = self.redis.ttl(key)
            result.append(item)
        return sorted(result, key=lambda x: x.get("login_at", ""), reverse=True)

    def count_sessions(self):
        return len(self.redis.keys("session:*"))
