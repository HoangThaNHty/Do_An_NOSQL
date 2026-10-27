"""Kiểm thử hồi quy luồng đọc tin, đăng ký và quản trị với DB Mongo riêng."""
import sys
import uuid
from pathlib import Path

import pytest
from bson import ObjectId
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import config
from data.article_catalog import build_catalog
from models import user as user_model


@pytest.fixture(scope="module")
def application():
    old_name = config.MONGO_DB_NAME
    name = "nosql_news_flow_test_" + uuid.uuid4().hex
    config.MONGO_DB_NAME = name
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    r = app.extensions["redis"]
    before = set(r.scan_iter())
    db = app.extensions["db"]
    user_model.create_user(db, "qa_admin", "qa_admin@example.test", "secret123", "Quản trị kiểm thử", "admin")
    try:
        yield app
    finally:
        MongoClient(config.MONGO_URI).drop_database(name)
        added = set(r.scan_iter()) - before
        if added:
            r.delete(*added)
        config.MONGO_DB_NAME = old_name


@pytest.fixture
def client(application):
    return application.test_client()


@pytest.fixture
def admin(client):
    assert client.post("/api/auth/login", json={"identifier": "qa_admin", "password": "secret123"}).status_code == 200
    return client


def article(title="Bài kiểm thử tiếng Việt", status="published", category="Công nghệ"):
    return {"title": title, "content": "Nội dung kiểm thử có dấu, đủ ý và dễ đọc.",
            "category": category, "status": status, "tags": ["kiểm thử"],
            "image": "/static/images/news_002.jpg"}


def test_saved_anonymous_and_brand(client):
    assert client.get('/api/saved').status_code == 401
    assert client.put('/api/saved/' + str(ObjectId())).status_code == 401
    assert client.delete('/api/saved/' + str(ObjectId())).status_code == 401
    assert client.get('/saved').status_code == 302
    for path, heading in (('/login', 'Chào mừng bạn'), ('/register', 'Bắt đầu cùng')):
        text = client.get(path).get_data(as_text=True)
        assert 'Điểm Tin' in text and heading in text
        assert 'Tin Tức NoSQL' not in text and 'hàm băm' not in text


def test_saved_set_isolation_persistence_and_visibility(admin, application):
    aid = admin.post('/api/articles', json=article('Bài để đọc sau')).json['data']['_id']
    draft = admin.post('/api/articles', json=article('Bản nháp riêng', status='draft')).json['data']['_id']
    uid = application.extensions['db'].users.find_one({'username': 'qa_admin'})['_id']
    key = 'user:saved:' + str(uid)
    r = application.extensions['redis']
    assert admin.put('/api/saved/not-valid').status_code == 400
    assert admin.put('/api/saved/' + str(ObjectId())).status_code == 404
    assert admin.put('/api/saved/' + draft).status_code == 404
    assert admin.put('/api/saved/' + aid, headers={'Origin': 'https://foreign.test'}).status_code == 403
    for _ in range(2):
        assert admin.put('/api/saved/' + aid, json={'user_id': 'someone-else'}).json['saved']
    assert r.type(key) == b'set' and r.scard(key) == 1 and r.ttl(key) == -1
    assert aid in [a['_id'] for a in admin.get('/api/saved').json['data']['items']]
    other = application.test_client()
    name = 'saved_' + uuid.uuid4().hex[:12]
    other.post('/api/auth/register', json={'username': name, 'email': name+'@example.test', 'password': 'secret123'})
    other.post('/api/auth/login', json={'identifier': name, 'password': 'secret123'})
    assert other.get('/api/saved').json['data']['total'] == 0
    other.delete('/api/saved/' + aid)
    assert r.scard(key) == 1
    admin.get('/logout')
    admin.post('/login?next=/saved', data={'identifier': 'qa_admin', 'password': 'secret123'})
    assert admin.get('/api/saved').json['data']['total'] == 1
    admin.put('/api/articles/' + aid, json={'status': 'draft'})
    assert admin.get('/api/saved').json['data']['total'] == 0
    admin.put('/api/articles/' + aid, json={'status': 'published'})
    assert admin.get('/api/saved').json['data']['total'] == 1
    admin.delete('/api/articles/' + aid)
    assert admin.get('/api/saved').json['data']['total'] == 0
    for _ in range(2):
        assert admin.delete('/api/saved/' + aid).json['saved'] is False
    assert r.scard(key) == 0


@pytest.mark.parametrize('target', ['/saved', '/articles/' + 'a'*24, '//evil.test', 'https://evil.test'])
def test_login_return_path(client, target):
    result = client.post('/login', query_string={'next': target}, data={'identifier': 'qa_admin', 'password': 'secret123'})
    assert result.location == (target if target.startswith('/saved') or target.startswith('/articles/') else '/')


def test_login_has_no_demo_credentials(client):
    text = client.get("/login").get_data(as_text=True)
    assert "Đăng nhập" in text
    assert all(value not in text for value in ("sv1_admin", "sv2_editor", "123456", "Tài khoản demo"))


def test_registration_creates_reader_and_blocks_admin(client):
    response = client.post("/api/auth/register", json={"username": "qa_reader", "email": "qa_reader@example.test",
                                                      "password": "secret123", "confirm_password": "secret123", "role": "admin"})
    assert response.status_code == 201
    assert response.json["data"]["role"] == "reader"
    client.post("/api/auth/login", json={"identifier": "qa_reader", "password": "secret123"})
    assert client.get("/admin/").status_code == 302
    assert client.post("/api/articles", json=article()).status_code == 403
    for path in ("stats", "keys", "sessions"):
        assert client.get("/api/cache/" + path).status_code == 403


@pytest.mark.parametrize("payload", [
    {"email": "bad-email"}, {"username": "tên có khoảng trắng"},
    {"password": "short", "confirm_password": "short"}, {"confirm_password": "mismatch"},
])
def test_invalid_registration(client, payload):
    base = {"username": "qa_invalid", "email": "qa_invalid@example.test", "password": "secret123", "confirm_password": "secret123"}
    assert client.post("/api/auth/register", json={**base, **payload}).status_code == 400


def test_duplicate_registration_is_rejected(client):
    data = {"username": "qa_duplicate", "email": "qa_duplicate@example.test", "password": "secret123"}
    assert client.post("/api/auth/register", json=data).status_code == 201
    assert client.post("/api/auth/register", json=data).status_code == 400


def test_admin_article_author_cache_edit_delete(admin, application):
    created = admin.post("/api/articles", json=article()).json["data"]
    aid = created["_id"]
    assert created["author"] is not None
    service = application.extensions["cache_service"]
    service.invalidate_article(aid)
    miss = admin.get("/api/articles/" + aid).json
    hit = admin.get("/api/articles/" + aid).json
    assert miss["source"] == "database" and hit["source"] == "cache"
    assert miss["data"] == hit["data"]
    assert admin.put("/api/articles/" + aid, json={"title": "Tiêu đề đã được sửa"}).status_code == 200
    assert not service.redis.exists(service.article_key(aid))
    updated = admin.get("/api/articles/" + aid).json
    assert updated["data"]["title"] == "Tiêu đề đã được sửa"
    assert updated["source"] == "database"
    assert admin.delete("/api/articles/" + aid).status_code == 200
    assert admin.get("/api/articles/" + aid).status_code == 404


def test_empty_edit_and_duplicate_titles(admin):
    one = admin.post("/api/articles", json=article("Trùng tiêu đề")).json["data"]
    two = admin.post("/api/articles", json=article("Một tiêu đề khác")).json["data"]
    response = admin.put("/api/articles/" + two["_id"], json={"title": "Trùng tiêu đề"})
    assert response.status_code == 200
    assert one["slug"] != response.json["data"]["slug"]
    assert admin.put("/api/articles/" + two["_id"], json={"content": "   "}).status_code == 400
    admin.put("/api/articles/" + two["_id"], json={"image_caption": "Ảnh mã nguồn"})
    changed = admin.put("/api/articles/" + two["_id"], json={"image": "/static/images/news_001.jpg"})
    assert changed.json["data"]["image_caption"] == ""


def test_draft_admin_visibility_and_public_privacy(admin, application):
    draft = admin.post("/api/articles", json=article("Bản nháp kiểm thử", "draft")).json["data"]
    assert "Bản nháp kiểm thử" in admin.get("/admin/articles").get_data(as_text=True)
    assert admin.get("/api/articles/" + draft["_id"]).status_code == 404
    result = admin.get("/api/articles/search?q=Bản%20nháp%20kiểm%20thử").json["data"]
    assert result["total"] == 0
    admin.put("/api/articles/" + draft["_id"], json={"status": "published"})
    assert admin.get("/api/articles/" + draft["_id"]).status_code == 200
    admin.put("/api/articles/" + draft["_id"], json={"status": "draft"})
    assert admin.get("/api/articles/" + draft["_id"]).status_code == 404


def test_list_cache_includes_page_size(admin):
    for i in range(8):
        admin.post("/api/articles", json=article(f"Phân trang số {i}"))
    large = admin.get("/api/articles?per_page=30").json["data"]
    small = admin.get("/api/articles?per_page=3").json["data"]
    assert large["per_page"] == 30 and len(large["items"]) > 3
    assert small["per_page"] == 3 and len(small["items"]) == 3
    second = admin.get("/api/articles?per_page=3&page=2").json["data"]
    assert not ({x["_id"] for x in small["items"]} & {x["_id"] for x in second["items"]})


def test_popular_uses_current_redis_counts_before_pagination(admin, application):
    service = application.extensions["article_service"]
    first = admin.post("/api/articles", json=article("Bài có lượt xem cao nhất")).json["data"]
    second = admin.post("/api/articles", json=article("Bài được xem tiếp theo")).json["data"]
    r = application.extensions["redis"]
    r.set(service.cache.views_key(first["_id"]), 700, ex=60)
    r.set(service.cache.views_key(second["_id"]), 500, ex=60)
    result = admin.get("/api/articles?sort=views&per_page=1").json["data"]
    assert result["items"][0]["_id"] == first["_id"]
    r.set(service.cache.views_key(second["_id"]), 800, ex=60)
    assert service.popular(1)[0]["_id"] == second["_id"]
    assert admin.get("/api/articles?sort=views&per_page=1&page=2").json["data"]["items"][0]["_id"] == first["_id"]


def test_related_excludes_self_drafts_and_other_categories(admin, application):
    for i in range(5):
        admin.post("/api/articles", json=article(f"Bài cùng mục {i}", category="Khoa học"))
    chosen = admin.post("/api/articles", json=article("Bài cần tìm liên quan", category="Khoa học")).json["data"]
    admin.post("/api/articles", json=article("Nháp cùng mục", "draft", "Khoa học"))
    result = application.extensions["article_service"].related(chosen)
    assert len(result) == 3
    assert all(x["_id"] != chosen["_id"] and x["status"] == "published" and x["category"] == "Khoa học" for x in result)


def test_login_replaces_expired_cookie_and_logout_removes_session(client, application):
    client.set_cookie("session_id", "expired-session")
    response = client.post("/api/auth/login", json={"identifier": "qa_admin", "password": "secret123"})
    sid = response.json["data"]["session_id"]
    assert client.get_cookie("session_id").value == sid
    session = client.get("/api/auth/session").json
    assert ObjectId.is_valid(session["data"]["user_id"])
    assert session["data"]["role"] == "admin"
    refreshed = client.get("/profile")
    assert "Max-Age=" in refreshed.headers["Set-Cookie"]
    client.post("/api/auth/logout")
    assert client.get_cookie("session_id") is None
    assert not application.extensions["session_service"].get_session(sid)
    assert client.get("/profile").status_code == 302


def test_catalog_has_100_distinct_articles_with_local_matching_images():
    catalog = build_catalog()
    assert len(catalog) == len({x["title"] for x in catalog}) == 100
    assert {x["category"] for x in catalog} == {"Công nghệ", "Kinh tế", "Thể thao", "Khoa học", "Xã hội", "Đời sống"}
    root = Path(__file__).resolve().parent.parent
    for entry in catalog:
        assert (root / entry["image"].lstrip("/")).is_file()
        assert entry["image_alt"] and entry["image_caption"]
        assert "\n\n" in entry["content"]
        assert 260 <= len(entry["content"].split()) <= 400
        assert "phục vụ việc đọc, tìm kiếm" not in entry["content"]
        assert entry["summary"] not in entry["content"]


def test_search_suggestions_relevance_filters_and_draft_privacy(admin):
    public = admin.post("/api/articles", json=article("Container tại cảng biển", category="Kinh tế")).json["data"]
    draft = admin.post("/api/articles", json=article("Container bản nháp riêng", "draft", "Kinh tế")).json["data"]
    for query in ("contaner", "cang bien", "vận tải"):
        result = admin.get("/api/articles/suggestions", query_string={"q": query}).json["data"]
        ids = [item["_id"] for item in result["items"]]
        assert public["_id"] in ids
        assert draft["_id"] not in ids
        assert len(ids) <= 5
        assert all("content" not in item for item in result["items"])
    filtered = admin.get("/api/articles/suggestions?q=container&category=Công%20nghệ").json["data"]
    assert filtered["total"] == 0
    assert admin.get("/api/articles/suggestions?q=c").json["data"]["items"] == []
    assert admin.get("/api/articles/search?q=contaner").json["data"]["total"] >= 1


def test_busy_cache_returns_retryable_503(admin, application, monkeypatch):
    created = admin.post("/api/articles", json=article("Kiểm tra chờ khóa")).json["data"]
    cache = application.extensions["cache_service"]
    monkeypatch.setattr(cache, "lock_wait_ms", 40)
    key = cache.lock_key(cache.article_key(created["_id"]))
    cache.redis.set(key, "test-other-owner", px=1000)
    response = admin.get("/api/articles/" + created["_id"])
    assert response.status_code == 503 and response.headers["Retry-After"] == "1"
    assert response.json["success"] is False
    html = admin.get("/articles/" + created["_id"])
    assert html.status_code == 503 and "Nội dung đang được tải" in html.get_data(as_text=True)
