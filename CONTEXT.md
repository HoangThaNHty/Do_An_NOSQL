# CONTEXT.md — BÀN GIAO DỰ ÁN CHO AI/MODEL KHÁC

> **Mục đích:** file này tổng hợp *toàn bộ* trạng thái dự án tại một thời điểm, để bất kỳ AI/model nào
> (hoặc người mới) đọc xong là làm việc tiếp được ngay, **không cần đọc lại lịch sử hội thoại**.
>
> **Cập nhật lần cuối:** 2026-10-26
> **Trạng thái:** ✅ Sản phẩm chạy được 100% — còn thiếu tài liệu nộp (báo cáo Word, slide PPT) và chia nhánh Git.

---

## 0. TL;DR — 10 dòng nắm được dự án

1. **Đề tài 06:** *Cache-Aside & Session Management* — web tin tức.
2. **Stack:** Flask 3.1 (Python 3.13) + **MongoDB 8** (DB gốc) + **Redis 8.10** (CSDL chính: cache/session/counter) + Bootstrap 5.
3. **Redis là "CSDL chính"** theo nghĩa: đồ án tập trung nghiên cứu Redis, và Redis là **source of truth** cho *session*, *lượt xem*, *thống kê hit/miss*.
4. **MongoDB là DB gốc:** lưu bền vững `users` + `articles`.
5. **Luồng đọc:** App → Redis (hit?) → miss → MongoDB → ghi ngược Redis + `EXPIRE` 300s.
6. **Dữ liệu hiện có:** 6 users, 100 articles (30 ảnh thật CC0), 47 key Redis (4 nhóm TTL).
7. **Phân quyền:** 3 role `admin` / `editor` / `reader`, mật khẩu chung `123456`.
8. **Test:** 20/20 pass. **Benchmark:** danh sách bài MongoDB 3.317ms vs Redis 0.198ms (**x16.8**).
9. **Chạy:** `data\start_redis.bat` → `.venv\Scripts\python app.py` → http://127.0.0.1:5000
10. **Còn lại:** báo cáo Word 50–60 trang, slide PPT, commit vào 3 nhánh feature (đang trống).

---

## 1. Trạng thái hiện tại (đã kiểm chứng)

| Hạng mục | Giá trị thực tế | Cách kiểm tra |
|---|---|---|
| MongoDB | `Running` @ `127.0.0.1:27017` | `Get-Service MongoDB` |
| Redis | `PONG` @ `127.0.0.1:6379`, DB 0 | `D:\Redis\redis-cli.exe ping` |
| App | `{"app":"ok","mongo":"ok","redis":"ok"}` | `curl http://127.0.0.1:5000/api/health` |
| Dữ liệu Mongo | `users=6`, `articles=100` | MongoDB Compass |
| Dữ liệu Redis | 47 key sau `seed_redis.py --reset` (sẽ giảm dần do TTL) | `redis-cli DBSIZE` |
| Test | **20 passed** (~2.7s) | `.venv\Scripts\python -m pytest tests/ -q` |
| Git | nhánh `main`, working tree sạch, **12 commit** | `git log --oneline` |
| Mã nguồn | ~3.359 dòng Python (không tính `.venv`) | — |

---

## 2. Công nghệ & phiên bản

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Frontend | HTML5, CSS3, **Bootstrap 5** (local, không CDN), JavaScript, Bootstrap Icons | Giao diện tin tức + admin |
| Backend | Python **3.13** + **Flask 3.1** (app factory + dependency injection) | REST API + nghiệp vụ |
| DB gốc | **MongoDB 8** + PyMongo | `users`, `articles` |
| Cache/Session | **Redis 8.10** (Windows portable tại `D:\Redis`) + redis-py | Cache, TTL, Session Hash, INCR |
| GUI | **MongoDB Compass 1.52** · **Redis Insight** | Demo trực quan |
| Test | pytest | 20 test |
| Đo hiệu năng | script Python + matplotlib | `docs/figures/` |

> ⚠️ Ràng buộc: **không đổi stack** (đề tài đã khai báo HTML5/CSS3/Bootstrap 5/JS). Không thêm React/Vue/Tailwind.

---

## 3. Cấu trúc thư mục (đã tinh gọn — MVC)

```
D:\Do_AN_NOSQL\
├── app.py                  # app factory, DI wiring, before_request session middleware, /api/health
├── config.py               # Config class đọc .env (Mongo/Redis/TTL/thư mục)
├── requirements.txt
├── .env                    # KHÔNG commit (đã gitignore)
├── .env.example            # mẫu cấu hình
├── README.md               # hướng dẫn nhanh
├── CONTEXT.md              # ← file này
│
├── models/            (3)  # MODEL — schema, index, chuyển đổi document
│   ├── __init__.py
│   ├── user.py             # ensure_indexes, hash/verify password (werkzeug scrypt)
│   └── article.py          # ensure_indexes, to_dict, slugify, utcnow
│
├── controllers/       (5)  # CONTROLLER — nhận request, gọi service, render/JSON
│   ├── __init__.py         # login_required, admin_required, admin_only_required, editor_required
│   ├── article_controller.py   # trang đọc + REST API bài viết
│   ├── auth_controller.py      # login/register/logout/profile + API auth
│   ├── admin_controller.py     # dashboard, CRUD admin, users, cache dashboard
│   └── cache_controller.py     # API cache: stats/keys/sessions/invalidate/reset
│
├── services/          (5)  # BUSINESS LOGIC
│   ├── __init__.py
│   ├── article_service.py  # _load_from_database (giả lập latency), _enrich_views, popular()
│   ├── cache_service.py    # ★ Cache-Aside, TTL/EXPIRE, invalidation, INCR views, get_views_many()
│   ├── session_service.py  # ★ Redis Hash session + TTL + sliding expiration
│   ├── auth_service.py     # đăng ký/đăng nhập, kiểm tra mật khẩu
│
├── views/             (15) # VIEW — Jinja2
│   ├── base.html           # topbar + navbar 6 chuyên mục + footer + badge role
│   ├── index.html, list.html, detail.html, search.html
│   ├── login.html, register.html, profile.html
│   ├── admin_dashboard.html, admin_articles.html, admin_article_form.html,
│   │   admin_users.html, admin_cache.html
│   ├── 404.html, 500.html
│   └── partials/_card.html # card bài viết dùng chung
│
├── static/
│   ├── css/style.css       # design system: token + component (navy #0F2A4A, orange #E8590C)
│   ├── js/main.js
│   ├── images/             # 30 ảnh .jpg thật (CC0/PDM) + CREDITS.md + credits.json
│   ├── fonts/              # 15 file Be Vietnam Pro (.woff2) + fonts.css → demo offline
│   └── vendor/             # Bootstrap 5 + Bootstrap Icons (local)
│
├── data/              (9 py + 3 bat)
│   ├── seed_articles.py    # 6 users + 100 bài viết, map ảnh theo chuyên mục
│   ├── seed_redis.py       # 47 key với 4 nhóm TTL
│   ├── fetch_images.py     # tải ảnh Openverse (chỉ CC0/PDM)
│   ├── build_fonts_css.py  # sinh static/fonts/fonts.css
│   ├── backup.py / restore.py   # backup MongoDB (JSON + mongodump)
│   ├── benchmark.py / plot_benchmark.py  # đo hiệu năng + vẽ biểu đồ
│   ├── check_roles.py      # bảng phân quyền 9 mục (9/9 OK)
│   ├── start_redis.bat     # bật Redis (an toàn khi stdin bị redirect)
│   ├── open_demo_env.bat   # 1 cú bấm: Mongo + Redis + Compass + Redis Insight + web
│   └── toggle_latency.bat  # on/off SIMULATED_DB_LATENCY_MS
│
├── tests/             (3)
│   ├── test_article.py, test_cache.py, test_session.py   # 20 test
│
└── docs/
    ├── ARCHITECTURE.md     # kiến trúc + bảng "GV hỏi → trả lời ở đâu"
    ├── DEMO_CHECKLIST.md   # 8 bước demo trực tiếp
    ├── DEMO_GUIDE.md       # hướng dẫn mở Compass/Redis Insight + phân quyền + xử lý sự cố
    ├── figures/            # 2 PNG + bang_so_sanh.md
    └── screenshots/        # 8 ảnh chụp giao diện
```

**Quy ước đã chốt:** `database/` + `scripts/` đã gộp thành **`data/`**; `static/uploads` → **`static/images`**; không có subfolder `views/admin/` (dùng tiền tố `admin_`).

---

## 4. Kiến trúc & luồng xử lý

### 4.1. Wiring (Dependency Injection) — `app.py`

```
create_app()
 ├── load Config
 ├── MongoClient → db "nosql_news" → ensure_indexes()
 ├── Redis client (decode_responses=True)
 ├── CacheService(redis, config)
 ├── ArticleService(db, cache_service)
 ├── SessionService(redis, config)
 ├── AuthService(db, session_service)
 ├── register blueprints: article, auth, admin, cache
 └── before_request: đọc cookie session_id → SessionService.get() → g.current_user
```

### 4.2. Cache-Aside (điểm ăn điểm chính)

```
GET /articles/<id>
  │
  ├─ CacheService.get_article(id)
  │     └─ HGETALL article:cache:<id>
  │           ├─ HIT  → INCR stats:cache:hits  → trả về ngay (~0.2ms)
  │           └─ MISS → INCR stats:cache:misses
  │                     → MongoDB find_one (giả lập ~200ms nếu bật latency)
  │                     → HSET article:cache:<id> + EXPIRE 300
  │                     → trả về
  └─ _enrich_views(): đọc article:views:<id> (Redis) đè lên field views
```

Response JSON có `"source": "cache" | "database"` để chứng minh bằng F12.

### 4.3. Cache Invalidation

`ArticleService.update_article()` / `delete_article()`:
1. ghi MongoDB trước (DB gốc là chân lý)
2. `DEL article:cache:<id>`, `DEL article:cache:hot:<id>`, xóa `article:list:*`
3. lần đọc kế tiếp → Cache Miss → nạp lại bản mới

### 4.4. Session (Redis Hash + sliding expiration)

```
POST /login
  → AuthService kiểm tra scrypt hash trong MongoDB
  → SessionService.create(user):
        HSET session:<64-hex>  user_id username email role full_name login_at ip user_agent
        EXPIRE session:<sid> 1800
        Set-Cookie: session_id=<sid>; HttpOnly; SameSite=Lax
  → mỗi request: nếu TTL < 1500s thì EXPIRE lại 1800 (sliding)
  → GET /logout: DEL session:<sid> + xóa cookie
```

### 4.5. Bộ đếm lượt xem

`INCR article:views:<id>` + `EXPIRE 86400` (chỉ set EXPIRE khi key chưa có TTL) — thao tác nguyên tử.
**Lưu ý:** field `views` trong MongoDB luôn = 0; **giá trị hiển thị lấy từ Redis**.

---

## 5. Redis — schema key (đây là "CSDL chính")

| Key pattern | Kiểu | TTL | Nội dung | Nơi tạo |
|---|---|---|---|---|
| `session:<sid>` | **Hash** | 1800s (sliding) | `user_id`, `username`, `email`, `role`, `full_name`, `login_at`, `ip`, `user_agent` | đăng nhập |
| `article:cache:<id>` | **Hash** | 300s | toàn bộ field bài viết (JSON value theo field) | Cache Miss |
| `article:cache:hot:<id>` | **Hash** | 1800s | bài "nóng" (nhiều lượt xem) | đọc bài nổi bật |
| `article:list:<page>:<sort>:<tag>` | **String** (JSON) | 60s | danh sách bài đã phân trang | trang danh sách |
| `article:views:<id>` | **String** (số) | 86400s | lượt xem, tăng bằng `INCR` | mở bài viết |
| `stats:cache:hits` | String | không TTL | số lần Cache Hit | mỗi lần hit |
| `stats:cache:misses` | String | không TTL | số lần Cache Miss | mỗi lần miss |

**47 key sau khi seed:** 15 `article:cache*` (10 thường + 5 hot) · 3 `article:list` · 15 `article:views` · 12 `session` (TTL so le 1800→60) · 2 `stats`.

Xem bằng: **Redis Insight** → `127.0.0.1:6379`, DB **0**, password trống → tab Browser.

---

## 6. MongoDB — schema (DB gốc)

### `users` (6 document)

| Field | Kiểu | Ghi chú |
|---|---|---|
| `_id` | ObjectId | |
| `username` | str | unique |
| `email` | str | unique |
| `password_hash` | str | **scrypt** (`werkzeug.generate_password_hash`) — không lưu mật khẩu gốc |
| `full_name` | str | |
| `role` | str | `admin` \| `editor` \| `reader` |
| `avatar` | null | |
| `created_at`, `last_login` | datetime | |

Index: `idx_users_email` (unique), `idx_users_username` (unique), `idx_users_role`.

### `articles` (100 document)

| Field | Kiểu | Ví dụ |
|---|---|---|
| `_id` | ObjectId | |
| `title` | str | "AI tạo sinh..." |
| `slug` | str | unique |
| `summary` | str | mô tả ngắn |
| `content` | str | nội dung đầy đủ (nhiều đoạn) |
| `image` | str | `/static/images/news_001.jpg` |
| `category` | str | 1 trong 6 chuyên mục |
| `tags` | list[str] | |
| `status` | str | `published` |
| `author` | ObjectId/null | |
| `author_name` | str | |
| `views` | int | **luôn 0** — xem mục 4.5 |
| `created_at`, `updated_at` | datetime | |

Index: `idx_articles_slug` (unique), `idx_articles_category_created` (compound `category`+`created_at`), `idx_articles_author`, `idx_articles_created`.

> Ghi chú kỹ thuật: docstring trong `models/article.py` có nhắc "title text" nhưng **code chưa tạo text index**;
> tìm kiếm hiện dùng `$regex` (không phân biệt hoa thường). Nếu cần `$text` thì phải thêm index — đừng mô tả sai trong báo cáo.

### 6 chuyên mục (thứ tự hiển thị)

`Cong nghe` · `Kinh te` · `The thao` · `Khoa hoc` · `Xa hoi` · `Doi song`
(phân bổ 17/17/17/17/16/16 = 100 bài, đã xen kẽ khi seed để trang chủ đa dạng)

---

## 7. Routes (đầy đủ, dump từ `url_map`)

| Method | Path | Endpoint | Quyền |
|---|---|---|---|
| GET | `/` | `article.index` | công khai |
| GET | `/articles` | `article.list_articles` | công khai |
| GET | `/articles/<article_id>` | `article.article_detail` | công khai |
| GET | `/login` · POST | `auth.login` | công khai |
| GET/POST | `/register` | `auth.register` | công khai |
| GET | `/logout` | `auth.logout` | đã đăng nhập |
| GET | `/profile` | `auth.profile` | đã đăng nhập |
| GET | `/admin/` | `admin.dashboard` | admin, editor |
| GET | `/admin/articles` | `admin.articles` | admin, editor |
| GET/POST | `/admin/articles/create` | `admin.create_article` | admin, editor |
| GET/POST | `/admin/articles/edit/<id>` | `admin.edit_article` | admin, editor |
| POST | `/admin/articles/delete/<id>` | `admin.delete_article` | admin, editor |
| GET | `/admin/users` | `admin.users` | **chỉ admin** |
| GET | `/admin/cache` | `admin.cache_dashboard` | admin, editor |
| GET | `/api/articles` | `article.api_list_articles` | công khai |
| GET | `/api/articles/search` | `article.api_search_articles` | công khai |
| GET | `/api/articles/<id>` | `article.api_get_article` | công khai |
| POST | `/api/articles` | `article.api_create_article` | **admin, editor** (`403` cho reader) |
| PUT | `/api/articles/<id>` | `article.api_update_article` | **admin, editor** |
| DELETE | `/api/articles/<id>` | `article.api_delete_article` | **admin, editor** |
| POST | `/api/auth/login` | `auth.api_login` | công khai |
| POST | `/api/auth/register` | `auth.api_register` | công khai |
| POST | `/api/auth/logout` | `auth.api_logout` | đã đăng nhập |
| GET | `/api/auth/session` | `auth.api_session` | đã đăng nhập |
| GET | `/api/cache/stats` | `cache.stats` | công khai (phục vụ demo) |
| GET | `/api/cache/keys` | `cache.keys` | công khai (phục vụ demo) |
| GET | `/api/cache/sessions` | `cache.sessions` | công khai (phục vụ demo) |
| POST | `/api/cache/invalidate/<id>` | `cache.invalidate` | công khai (phục vụ demo) |
| POST | `/api/cache/reset` | `cache.reset` | công khai (phục vụ demo) |
| GET | `/api/health` | `health` | công khai |

---

## 8. Phân quyền & tài khoản test

### 8.1. Decorator (`controllers/__init__.py`)

| Decorator | Cho phép | Hành vi khi bị chặn |
|---|---|---|
| `login_required` | đã đăng nhập | HTML → redirect `/login`; API → `401` |
| `admin_required` | `admin`, `editor` | flash + redirect trang chủ |
| `admin_only_required` | **chỉ `admin`** | flash "Chỉ quản trị viên…" + về dashboard |
| `editor_required` | `admin`, `editor` | API → **`403`** (không redirect) |

### 8.2. Tài khoản (mật khẩu chung `123456`)

| Tài khoản | Email | Role | Dùng để |
|---|---|---|---|
| `admin` | admin@uit.edu.vn | `admin` | Test toàn quyền |
| `editor` | editor@uit.edu.vn | `editor` | Test quyền nội dung |
| `reader` | reader@uit.edu.vn | `reader` | Test quyền chỉ đọc |
| `sv1_admin` | sv1@uit.edu.vn | `admin` | Tài khoản SV1 |
| `sv2_editor` | sv2@uit.edu.vn | `editor` | Tài khoản SV2 |
| `sv3_editor` | sv3@uit.edu.vn | `editor` | Tài khoản SV3 |

Đăng nhập bằng **username hoặc email** đều được. Navbar hiển thị **badge role**.

### 8.3. Bảng phân quyền (chạy `data\check_roles.py` → 9/9 OK)

| Chức năng | admin | editor | reader |
|---|:---:|:---:|:---:|
| Trang chủ / danh sách / chi tiết | 200 | 200 | 200 |
| `/profile` | 200 | 200 | 200 |
| `/admin/` | 200 | 200 | **302** (đẩy ra) |
| `/admin/articles` | 200 | 200 | 302 |
| `/admin/articles/create` | 200 | 200 | 302 |
| `/admin/users` | 200 | **302** | 302 |
| `/admin/cache` | 200 | 200 | 302 |
| `POST /api/articles` | **201** | **201** | **403** |

> 2 lỗi phân quyền đã từng tồn tại và **đã sửa**: (1) reader tạo được bài qua API → thêm `@editor_required`;
> (2) editor xem được danh sách user → tách `@admin_only_required`.

---

## 9. Cấu hình (`.env` — copy từ `.env.example`)

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key` | Flask session cookie |
| `FLASK_DEBUG` | `0` | bật debug |
| `PORT` | `5000` | cổng web |
| `MONGO_URI` | `mongodb://127.0.0.1:27017` | DB gốc |
| `MONGO_DB_NAME` | `nosql_news` | tên DB |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` | `127.0.0.1` / `6379` / `0` | Redis |
| `REDIS_PASSWORD` | (trống) | demo nội bộ |
| `TTL_ARTICLE_CACHE` | `300` | cache bài viết |
| `TTL_ARTICLE_CACHE_HOT` | `1800` | bài nóng |
| `TTL_ARTICLE_LIST` | `60` | danh sách |
| `TTL_SESSION` | `1800` | phiên đăng nhập |
| `TTL_VIEWS` | `86400` | bộ đếm lượt xem |
| `SIMULATED_DB_LATENCY_MS` | `0` | **>0 để giả lập MongoDB ở xa** (demo 200ms) |

Đổi `.env` → **phải restart app**. Bật/tắt nhanh: `data\toggle_latency.bat on|off`.

---

## 10. Chạy & demo

### 10.1. Lệnh tối thiểu (VS Code terminal)

```powershell
cd D:\Do_AN_NOSQL
data\start_redis.bat          # bật Redis (báo PONG nếu đã chạy)
.venv\Scripts\python app.py   # → http://127.0.0.1:5000
```

### 10.2. Mở trọn môi trường demo (1 cú bấm)

```bat
data\open_demo_env.bat
```
→ bật MongoDB (nếu tắt) → bật Redis → mở **MongoDB Compass** → mở **Redis Insight** → mở web `/` và `/admin/cache`.

| GUI | Kết nối | Xem gì |
|---|---|---|
| **MongoDB Compass 1.52** | `mongodb://127.0.0.1:27017` → `nosql_news` | `users` (6), `articles` (100), filter/sort/index |
| **Redis Insight** | `127.0.0.1:6379`, DB 0, pass trống | `session:*` (Hash + TTL đếm lùi), `article:cache:*`, `article:views:*`, `stats:*` |

### 10.3. Nạp lại dữ liệu

```powershell
.venv\Scripts\python data\seed_articles.py --reset   # 6 users + 100 bài + ảnh
.venv\Scripts\python data\seed_redis.py --reset      # 47 key, 4 nhóm TTL
```

### 10.4. Kịch bản demo 8 bước

Xem **`docs/DEMO_CHECKLIST.md`**. Bản đầy đủ (mở GUI, lệnh CLI, xử lý sự cố, câu hỏi GV):
**`docs/DEMO_GUIDE.md`**.

---

## 11. Script trong `data/`

| Script | Chức năng |
|---|---|
| `seed_articles.py --reset` | tạo 6 user + 100 bài viết; map ảnh theo chuyên mục qua `credits.json` |
| `seed_redis.py --reset` | tạo 47 key (cache/list/views/session/stats) với TTL so le |
| `fetch_images.py` | tải ảnh từ **Openverse API**, chỉ nhận **CC0/PDM**, 16:9, 1200×675, ~130KB |
| `build_fonts_css.py` | sinh `static/fonts/fonts.css` cho 16 file woff2 |
| `backup.py` / `restore.py --latest --drop` | backup/restore MongoDB (JSON + `mongodump`) |
| `benchmark.py --n 200 --http http://127.0.0.1:5000` | đo MongoDB vs Redis (thô + qua HTTP) |
| `plot_benchmark.py` | vẽ `docs/figures/*.png` |
| `check_roles.py` | in bảng phân quyền 9 mục, so với kỳ vọng |
| `start_redis.bat` | bật Redis an toàn (dùng `Start-Process`, không dùng `start`) |
| `open_demo_env.bat` | mở toàn bộ môi trường demo |
| `toggle_latency.bat on\|off` | đổi `SIMULATED_DB_LATENCY_MS=200\|0` |

---

## 12. Kiểm thử & kết quả đo

### 12.1. Test — 20/20 pass

```powershell
.venv\Scripts\python -m pytest tests/ -q
# ....................  [100%]  20 passed in ~2.7s
```

Phạm vi: CRUD bài viết, Cache-Aside (hit/miss), TTL, invalidation, session create/get/destroy, sliding expiration.

### 12.2. Benchmark (`docs/figures/bang_so_sanh.md`)

| Kịch bản | MongoDB (ms) | Redis (ms) | Redis nhanh hơn |
|---|---|---|---|
| Chi tiết bài viết | 0.531 | 0.205 | x2.6 |
| **Danh sách bài viết** | **3.317** | **0.198** | **x16.8** |
| Tìm kiếm | 1.099 | 0.270 | x4.1 |
| Chi tiết (mô phỏng RTT 50ms) | 51.616 | 0.295 | **x175.0** |
| HTTP request (tab Network) | 14.576 | 8.686 | x1.7 |

Biểu đồ: `docs/figures/bieu_do_hieu_nang.png`, `bieu_do_phan_bo.png`.

> Khi demo, bật `toggle_latency.bat on` để có số ~268ms (MISS) → ~10ms (HIT) như kịch bản đề tài.

---

## 13. Tài liệu hiện có

| File | Nội dung |
|---|---|
| `README.md` | tổng quan + cài đặt + API + nhánh Git |
| `docs/ARCHITECTURE.md` | kiến trúc chi tiết + bảng **"GV hỏi → trả lời ở đâu"** |
| `docs/DEMO_CHECKLIST.md` | 8 bước demo trực tiếp, chia vai SV1/SV2/SV3 |
| `docs/DEMO_GUIDE.md` | mở Compass/Redis Insight, tài khoản 3 role, lệnh CLI, xử lý sự cố |
| `docs/figures/` | 2 biểu đồ PNG + bảng số |
| `docs/screenshots/` | 8 ảnh giao diện (dùng cho báo cáo) |
| `static/images/CREDITS.md` | nguồn + giấy phép 30 ảnh |

---

## 14. Git

| Nhánh | Trạng thái | Phạm vi dự kiến |
|---|---|---|
| `main` | 12 commit, sạch | bản tích hợp để demo |
| `feature/database-article-crud` | chỉ có commit khởi tạo | MongoDB, model, CRUD, admin (SV1) |
| `feature/redis-cache` | chỉ có commit khởi tạo | Cache-Aside, TTL, invalidation, INCR (SV2) |
| `feature/session-performance` | chỉ có commit khởi tạo | Auth, session Redis, backup, benchmark (SV3) |

**Việc còn lại:** tách commit thật vào 3 nhánh (cần tên/MSSV 3 thành viên). `.env` đã gitignore đúng.

---

## 15. Quy ước & bẫy kỹ thuật (đọc kỹ trước khi sửa)

1. **UTF-8 tiếng Việt:** TUYỆT ĐỐI không dùng `PowerShell -replace` / `Set-Content` lên file có tiếng Việt
   (gây mojibake). Dùng **Python** với `encoding="utf-8"`, hoặc công cụ `edit` của agent.
2. **Redis là bộ nhớ tạm:** nếu tắt cứng (`shutdown nosave`) sẽ mất key → chạy lại `seed_redis.py --reset`.
   RDB nằm ở `D:/Redis/data/dump.rdb`.
3. **Không dùng `start` trong .bat** khi có thể bị redirect stdin → dùng
   `powershell -NoProfile -Command "Start-Process ..."`. Không dùng `timeout /t` (lỗi khi pipe) → dùng `ping -n`.
4. **Đường dẫn ảnh:** `/static/images/...` (không phải `/static/uploads/` cũ).
5. **Bootstrap/font là local:** không thêm CDN — demo phải chạy offline.
6. **Đổi `.env` phải restart app** (config đọc lúc khởi động).
7. **Sửa bài viết phải xóa cache** — nếu quên, test `test_cache` sẽ fail.
8. **`views` trong MongoDB luôn 0** — đừng "sửa" thành cập nhật Mongo, vì thiết kế là Redis giữ bộ đếm.
9. **Không commit `.env`**, không commit `.venv`, `__pycache__`, `.pytest_cache`.
10. File `d? tài 6.docx` ở thư mục gốc bị lỗi tên/encoding từ trước — **không tự ý đổi tên** khi chưa hỏi user.

---

## 16. Việc còn lại (backlog)

| # | Việc | Phụ thuộc | Ghi chú |
|---|---|---|---|
| 1 | **Báo cáo Word 50–60 trang** | tên 3 SV (có thể dùng `SV1/SV2/SV3`) | nguyên liệu đã đủ: 8 ảnh, 3 biểu đồ, số đo, sơ đồ |
| 2 | **Slide PPT 10–12 trang** | làm sau báo cáo | bám 8 bước demo |
| 3 | **Chia commit vào 3 nhánh** | tên/MSSV | hiện nhánh trống |
| 4 | (tùy chọn) mở rộng 30 → 60 ảnh | — | ~8MB, 8–10 ảnh/chuyên mục |
| 5 | (tùy chọn) thêm text index `title` | — | nếu báo cáo có nói "tìm kiếm toàn văn" |
| 6 | (tùy chọn) role `moderator` duyệt `draft → published` | — | hiện `status` có nhưng chưa tách quyền |

---

## 17. Câu hỏi giảng viên hay hỏi → trả lời ở đâu

| Câu hỏi | Trả lời tại |
|---|---|
| Cache-Aside hoạt động thế nào? | `services/cache_service.py` → `get_article()`; mục 4.2 file này |
| TTL đặt ở đâu? | `config.py` (`TTL_*`), mục 9 |
| Sửa bài thì cache xử lý sao? | `services/article_service.py` → invalidate; mục 4.3 |
| Session lưu gì, ở đâu? | `services/session_service.py` (`HSET session:<sid>` + `EXPIRE`); mục 4.4 |
| Mật khẩu an toàn không? | `models/user.py` → `werkzeug` scrypt |
| Lượt xem đếm thế nào? | `cache_service.incr_views()` → `INCR`; mục 4.5 |
| Phân quyền ở đâu? | `controllers/__init__.py` (4 decorator); mục 8 |
| Vì sao "CSDL chính là Redis" mà đọc từ Mongo? | mục 0 + mục 5: Redis giữ session/views/stats; Mongo giữ nội dung |
| Sao `views` trong Mongo luôn 0? | mục 4.5 / 15.8 |
| Backup/Restore? | `data/backup.py`, `data/restore.py` |
| Đo hiệu năng ra sao? | `data/benchmark.py`, `data/plot_benchmark.py`, mục 12.2 |
| Có test không? | `tests/` — 20 test, mục 12.1 |

---

## 18. Nếu bạn là AI đọc file này — hãy làm theo

1. **Không đổi stack**, không thêm framework frontend.
2. **Không sửa file tiếng Việt bằng PowerShell** (mục 15.1).
3. Trước khi sửa logic cache/session: đọc `services/cache_service.py` + `services/session_service.py` + chạy `pytest` để có baseline 20/20.
4. Sau khi sửa: chạy `pytest`, `data/check_roles.py`, và `curl /api/health` — cả 3 phải xanh.
5. Việc ưu tiên hiện tại: **báo cáo Word → slide PPT → chia nhánh Git** (mục 16).
6. Nếu cần tên thành viên mà chưa có: dùng `SV1/SV2/SV3` và ghi chú rõ để thay sau.
