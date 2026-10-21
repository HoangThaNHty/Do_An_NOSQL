"""
tests/test_article.py - KIEM THU CRUD BAI VIET tren DB goc (MongoDB)

Chay:  python -m pytest tests/ -v
"""

import sys
from pathlib import Path

import pytest
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402
from models import article as article_model  # noqa: E402
from models import user as user_model  # noqa: E402

TEST_DB_NAME = "nosql_news_test"


@pytest.fixture(scope="module")
def db():
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    database = client[TEST_DB_NAME]
    user_model.ensure_indexes(database)
    article_model.ensure_indexes(database)
    yield database
    client.drop_database(TEST_DB_NAME)
    client.close()


@pytest.fixture
def sample_article():
    return {
        "title": "Bai viet kiem thu CRUD",
        "summary": "Tom tat bai viet kiem thu",
        "content": "Noi dung kiem thu CRUD tren MongoDB.",
        "image": "/static/uploads/news_001.jpg",
        "category": "Cong nghe",
        "tags": ["kiem thu", "crud"],
        "status": "published",
    }


def test_create_article(db, sample_article):
    doc = article_model.create_article(db, sample_article, author_name="Tester")
    assert doc["_id"] is not None
    assert doc["title"] == sample_article["title"]
    assert doc["slug"] == "bai-viet-kiem-thu-crud"
    assert doc["views"] == 0
    assert doc["author_name"] == "Tester"


def test_get_article(db, sample_article):
    doc = article_model.create_article(db, sample_article)
    found = article_model.get_article(db, str(doc["_id"]))
    assert found is not None
    assert found["title"] == sample_article["title"]
    assert article_model.get_article(db, "khong-phai-id-hoan-chinh") is None


def test_update_article(db, sample_article):
    doc = article_model.create_article(db, sample_article)
    updated = article_model.update_article(db, str(doc["_id"]), {"title": "Tieu de da sua"})
    assert updated["title"] == "Tieu de da sua"
    assert updated["slug"] == "tieu-de-da-sua"
    assert updated["updated_at"] is not None


def test_delete_article(db, sample_article):
    doc = article_model.create_article(db, sample_article)
    assert article_model.delete_article(db, str(doc["_id"])) is True
    assert article_model.get_article(db, str(doc["_id"])) is None
    assert article_model.delete_article(db, str(doc["_id"])) is False


def test_list_articles_pagination(db, sample_article):
    for i in range(15):
        data = dict(sample_article)
        data["title"] = f"Bai viet so {i}"
        article_model.create_article(db, data)
    result = article_model.list_articles(db, page=1, per_page=5)
    assert len(result["items"]) == 5
    assert result["total"] >= 15
    assert result["has_next"] is True
    assert result["has_prev"] is False


def test_search_by_keyword(db, sample_article):
    data = dict(sample_article)
    data["title"] = "MongoDB replica set va cach sao chep du lieu"
    article_model.create_article(db, data)
    result = article_model.list_articles(db, keyword="replica")
    assert result["total"] >= 1


def test_filter_by_category(db, sample_article):
    article_model.create_article(db, sample_article)
    result = article_model.list_articles(db, category="Cong nghe")
    assert result["total"] >= 1
    result = article_model.list_articles(db, category="The thao")
    assert result["total"] == 0


def test_user_password_hash(db):
    user_model.create_user(db, "tester", "tester@test.vn", "matkhau123", "Tester")
    user = user_model.find_by_email(db, "tester@test.vn")
    assert user is not None
    assert user["password_hash"] != "matkhau123"  # mat khau da duoc hash
    assert user_model.verify_password(user, "matkhau123") is True
    assert user_model.verify_password(user, "sai-mat-khau") is False
