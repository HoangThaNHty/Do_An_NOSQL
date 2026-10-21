"""
config.py - Cau hinh chung cho toan bo du an (Doi duong voi appsettings.json cua ASP.NET Core)

Moi thu so voi thoi gian / bien mau deu doc tu file .env de khong roi mat khau
vao ma nguon (khong commit file .env len GitHub).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Thu muc goc cua du an
BASE_DIR = Path(__file__).resolve().parent

# Nap bien tu .env (duong dan tuyet doi cho ca May)
load_dotenv(BASE_DIR / ".env")


class Config:
    """Cau hinh mac dinh cho moi truong (dev / demo)."""

    # ---------------- Flask ----------------
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    PORT = int(os.getenv("PORT", 5000))

    # ---------------- MongoDB (DB goc) ----------------
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "nosql_news")

    # ---------------- Redis (Cache + Session) ----------------
    REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

    # ---------------- TTL (giay) ----------------
    # Cache bai viet: 5 phut
    TTL_ARTICLE_CACHE = int(os.getenv("TTL_ARTICLE_CACHE", 300))
    # Bai "nong" giu cache lau hon: 30 phut
    TTL_ARTICLE_CACHE_HOT = int(os.getenv("TTL_ARTICLE_CACHE_HOT", 1800))
    # Cache danh sach bai viet: 1 phut
    TTL_ARTICLE_LIST = int(os.getenv("TTL_ARTICLE_LIST", 60))
    # Session dang nhap: 30 phut
    TTL_SESSION = int(os.getenv("TTL_SESSION", 1800))
    # Bo dem luot xem: 1 ngay
    TTL_VIEWS = int(os.getenv("TTL_VIEWS", 86400))

    # ---------------- Giao dien ----------------
    PER_PAGE = 9
    SITE_NAME = "Tin Tuc NoSQL"

    # ---------------- Mo phong do tre mang (chi dung khi demo) ----------------
    # Khi MongoDB nam o may khac, moi lan doc deu phai trai qua 1 lan
    # round-trip mang. Bai toan deu yeu cau "doc DB goc ~200ms, doc Redis <5ms".
    # Dat gia tri nay (vd 200) de mô phỏng do tre mang khi demo tren may
    # tinh cuc bo. DAT VE 0 khi do hieu nang that.
    SIMULATED_DB_LATENCY_MS = int(os.getenv("SIMULATED_DB_LATENCY_MS", 0))

    # ---------------- Thu muc ----------------
    IMAGES_FOLDER = BASE_DIR / "static" / "images"
    STATIC_FOLDER = BASE_DIR / "static"
    DATA_FOLDER = BASE_DIR / "data"
    # ten cu (giu lai de khong phai doi ma cu)
    UPLOAD_FOLDER = IMAGES_FOLDER


config = Config()
