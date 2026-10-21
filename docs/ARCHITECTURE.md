# KIẾN TRÚC HỆ THỐNG — ĐỀ TÀI 06
## Phân hệ Caching bài viết & Quản lý phiên (Session Management)

> Tài liệu này là **bản đồ tra cứu**: khi thầy giáo hỏi "phần này nằm ở đâu trong code",
> tra bảng mục 7 là ra ngay. Dùng để ôn trước buổi bảo vệ.

---

## 1. Tổng quan hệ thống

```
        ┌──────────────────────┐
        │   Trình duyệt        │  HTML5 / CSS3 / Bootstrap 5 / JavaScript
        │  (Chrome, F12)       │
        └──────────┬───────────┘
                   │ HTTP (GET/POST) + Cookie (session_id)
                   ▼
        ┌──────────────────────────────────────────────┐
        │           Flask Application (app.py)          │
        │  ┌────────────────────────────────────────┐  │
        │  │ CONTROLLER  (controllers/)             │  │
        │  │  article_controller / auth_controller  │  │
        │  │  admin_controller / cache_controller   │  │
        │  └───────────────────┬────────────────────┘  │
        │                      ▼                       │
        │  ┌────────────────────────────────────────┐  │
        │  │ SERVICE  (services/)                   │  │
        │  │  article_service  → cache_service      │  │
        │  │  auth_service    → session_service     │  │
        │  └──────────┬──────────────────────┬──────┘  │
        │             ▼                      ▼         │
        │  ┌──────────────────┐  ┌────────────────────┐ │
        │  │ MODEL            │  │  MODEL (Redis)     │ │
        │  │ (models/)        │  │  cache + session   │ │
        │  │  article / user  │  │                    │ │
        │  └────────┬─────────┘  └─────────┬──────────┘ │
        └───────────┼──────────────────────┼────────────┘
                    ▼                      ▼
        ┌────────────────────┐   ┌──────────────────────┐
        │  MongoDB (DB goc)  │   │  Redis               │
        │  users, articles   │   │  cache + session     │
        │  + MongoDB Compass │   │  + Redis Insight     │
        └────────────────────┘   └──────────────────────┘
```

**Quy trình đọc một bài viết:**
Browser → Controller → Service (`cache_service.get_article`) → **Redis trước** →
nếu HIT thì trả về ngay; nếu MISS thì đọc MongoDB rồi ghi ngược lại Redis kèm TTL.

---

## 2. Mô hình tổ chức code: Kiến trúc 3 tầng (Layered) kết hợp MVC

Flask không phải framework MVC cứng như Rails/Spring, nên dự án tổ chức theo
**kiến trúc 3 tầng** — tương đương cách ASP.NET Core tổ chức:

| Tầng | Thư mục | Trách nhiệm | Đối chiếu ASP.NET Core |
|---|---|---|---|
| **Presentation** | `views/` + `static/` + `controllers/` | Nhận request, render HTML, điều hướng | `Views/` + `wwwroot/` + `Controllers/` |
| **Business Logic** | `services/` | Luật nghiệp vụ: Cache-Aside, TTL, Session, Invalidation | `Services/` |
| **Data Access** | `models/` + `config.py` + `database/` | Định nghĩa dữ liệu, truy vấn, index, seed, backup | `Models/` + `Data/` + `appsettings.json` |

**Cách trả lời khi thầy hỏi "dự án bạn tổ chức theo mô hình gì?":**
> *"Dự án tổ chức theo kiến trúc 3 tầng kết hợp mô hình MVC. Tầng Presentation gồm
> Controller (Flask Blueprint) và View (Jinja2 template). Tầng Business Logic chứa các
> Service, là nơi hiện thực hóa Cache-Aside và quản lý Session. Tầng Data Access chứa
> Model định nghĩa dữ liệu và truy vấn MongoDB. Tách tầng như vậy giúp phần cache
> không phụ thuộc trực tiếp vào giao diện, nên thay đổi giao diện không ảnh hưởng logic cache."*

---

## 3. Cấu trúc thư mục và trách nhiệm từng file

```
D:\Do_AN_NOSQL\
├── app.py                       # Điểm khởi chạy: App Factory, DI, middleware, /api/health
├── config.py                    # Cấu hình: Mongo URI, Redis, TTL, biến môi trường
├── requirements.txt             # Thư viện + phiên bản
├── .env / .env.example          # Cấu hình thật (KHÔNG commit) / mẫu
├── .gitignore / README.md
│
├── models/                      # MODEL — dữ liệu & truy vấn MongoDB
│   ├── user.py                  #   Schema User, index email/username, hash mật khẩu
│   └── article.py               #   Schema Article, index, CRUD, tìm kiếm/lọc/sắp xếp/phân trang
│
├── controllers/                 # CONTROLLER — nhận request, gọi service, trả kết quả
│   ├── article_controller.py    #   Trang chủ, danh sách, chi tiết + API CRUD bài viết
│   ├── auth_controller.py       #   Đăng ký / đăng nhập / đăng xuất / profile + API auth
│   ├── admin_controller.py      #   Trang quản trị: thêm / sửa / xóa bài viết, danh sách user
│   └── cache_controller.py      #   API theo dõi cache: stats, sessions, keys, invalidate
│
├── services/                    # BUSINESS LOGIC — trung tâm đề tài
│   ├── article_service.py       #   Nghiệp vụ bài viết, gọi cache (Cache-Aside + Invalidation)
│   ├── cache_service.py         # ★ Cache-Aside, TTL/EXPIRE, Cache Invalidation, INCR lượt xem
│   ├── session_service.py       # ★ Session lưu dạng Hash trên Redis + EXPIRE, sliding expiration
│   └── auth_service.py          #   Đăng ký, xác thực mật khẩu
│
├── views/                       # VIEW — Jinja2 template (phẳng, không subfolder)
│   ├── base.html                #   Layout chung: navbar đổi theo trạng thái session, flash
│   ├── index.html               #   Trang chủ
│   ├── articles.html            #   Danh sách + tìm kiếm + lọc + sắp xếp + phân trang
│   ├── article_detail.html      #   Chi tiết + hiển thị lượt xem + badge nguồn dữ liệu
│   ├── login.html / register.html / profile.html
│   ├── admin_dashboard.html     #   Thống kê: bài viết, user, session, key Redis, hit/miss
│   ├── admin_articles.html      #   Bảng quản lý bài viết (sửa / xóa)
│   ├── admin_article_form.html  #   Form thêm / sửa bài viết
│   ├── admin_users.html         #   Danh sách người dùng
│   └── 404.html
│
├── static/
│   ├── css/style.css            # CSS riêng của dự án
│   ├── js/main.js               # Xác nhận xóa, tự ẩn thông báo, cập nhật số liệu cache
│   ├── uploads/                 # 100 ảnh bài viết (sinh bằng Pillow)
│   └── vendor/                  # Bootstrap 5 + Icons (tải về local, demo không cần mạng)
│
├── database/
│   ├── seed_articles.py         # Tạo 3 user demo + 100 bài viết + 100 ảnh
│   ├── seed_redis.py            # Tạo 50 key Redis với TTL khác nhau (20–50 theo yêu cầu)
│   ├── backup.py                # Backup MongoDB (JSON) + Redis (key + TTL)
│   └── restore.py               # Khôi phục từ file backup
│
├── scripts/
│   ├── benchmark.py             # Đo thời gian MongoDB vs Redis (3–5 kịch bản)
│   ├── plot_benchmark.py        # Vẽ biểu đồ matplotlib (Chương 8)
│   ├── start_redis.bat          # Bật Redis server
│   └── toggle_latency.bat       # Bật/tắt mô phỏng độ trễ mạng khi demo
│
├── tests/
│   ├── test_article.py          # Test CRUD MongoDB, tìm kiếm, lọc, phân trang
│   ├── test_cache.py            # Test Cache Hit/Miss, TTL, Invalidation, INCR
│   └── test_session.py          # Test tạo/đọc/gia hạn/xóa session Hash
│
└── docs/
    ├── ARCHITECTURE.md          # ← tài liệu này
    ├── DEMO_CHECKLIST.md        # 8 bước demo theo kịch bản đề tài
    └── figures/                 # Biểu đồ kết quả benchmark
```

### Quy tắc "tra cứu 5 giây" khi thầy hỏi

| Thầy hỏi về | Trả lời ở file |
|---|---|
| Giao diện hiển thị | `views/` + `static/` |
| Đường đi của một request | `controllers/` → `services/` → `models/` |
| Luật cache / TTL / Invalidation / INCR | `services/cache_service.py` |
| Session trên Redis | `services/session_service.py` |
| Dữ liệu, index, truy vấn nâng cao | `models/article.py` |
| Kết nối DB, TTL, cấu hình | `config.py` + `app.py` |
| Dữ liệu mẫu, backup | `database/` |
| Đo hiệu năng, biểu đồ | `scripts/` |

---

## 4. Quy ước Redis key (hợp đồng chung của nhóm)

| Key | Kiểu dữ liệu | TTL | Ý nghĩa |
|---|---|---|---|
| `session:<session_id>` | **Hash** | 1800s | Phiên đăng nhập (HSET + EXPIRE) |
| `article:cache:<id>` | **Hash** | 300s | Cache nội dung bài viết (Cache-Aside) |
| `article:cache:hot:<id>` | **Hash** | 1800s | Bài "nóng" giữ cache lâu hơn |
| `article:list:<page>:<sort>:<filter>` | **String** (JSON) | 60s | Cache danh sách bài viết |
| `article:views:<id>` | **String** (counter) | 86400s | Bộ đếm lượt xem — tăng bằng **INCR** |
| `stats:cache:hits` | String (counter) | — | Số lần Cache Hit |
| `stats:cache:misses` | String (counter) | — | Số lần Cache Miss |

**Cấu trúc Hash của Session:**

```
HSET session:<sid> user_id     <ObjectId>
                   username    <tên đăng nhập>
                   email       <email>
                   full_name   <họ tên>
                   role        admin|editor|reader
                   login_at    2026-10-21 08:30:00
                   ip          127.0.0.1
                   user_agent  Mozilla/5.0 ...
EXPIRE session:<sid> 1800
```

---

## 5. Mô hình dữ liệu MongoDB

```jsonc
// collection: users
{
  "_id": ObjectId, "username": "sv1_admin", "email": "sv1@uit.edu.vn",
  "password_hash": "scrypt:16384:8:1$...",   // hash, KHÔNG lưu mật khẩu gốc
  "full_name": "SV1 - Data Architect", "role": "admin|editor|reader",
  "avatar": null, "created_at": ISODate, "last_login": ISODate
}

// collection: articles
{
  "_id": ObjectId, "title": "…", "slug": "cong-nghe-ai-…",
  "summary": "…", "content": "…",
  "image": "/static/uploads/news_001.jpg",   // ảnh thật trong DB gốc
  "category": "Cong nghe|Kinh te|The thao|Khoa hoc|Xa hoi|Doi song",
  "tags": ["…"], "status": "published|draft",
  "author": ObjectId, "author_name": "…",
  "views": 0,                                // giá trị khởi tạo; hiển thị lấy từ Redis
  "created_at": ISODate, "updated_at": ISODate
}
```

**Index đã tạo (để truy vấn nâng cao chạy nhanh):**

| Collection | Index | Dùng cho |
|---|---|---|
| users | email (unique), username (unique), role | Đăng nhập, quản lý user |
| articles | slug (unique) | Tìm theo slug |
| articles | category + created_at (compound) | Lọc chuyên mục + sắp xếp mới nhất |
| articles | author, created_at | Truy vấn theo tác giả, phân trang |

---

## 6. Ba luồng xử lý quan trọng (để giải thích khi bị hỏi)

### Luồng A — Đọc bài viết (Cache-Aside) — `services/cache_service.py::get_article`

```
GET /articles/<id>
 └─ controllers/article_controller.py
     └─ services/article_service.py::get_detail
         └─ services/cache_service.py::get_article(id, loader)
             ├─ HGETALL article:cache:<id>
             │    ├─ có dữ liệu → CACHE HIT  → INCR stats:cache:hits → trả về
             │    └─ không có   → CACHE MISS → INCR stats:cache:misses
             │         └─ loader() → MongoDB find_one
             │         └─ HSET article:cache:<id> + EXPIRE 300
             └─ INCR article:views:<id>  (bộ đếm lượt xem)
```

### Luồng B — Sửa bài viết (Cache Invalidation) — `services/article_service.py::update`

```
PUT /api/articles/<id>  (hoặc form trong /admin/articles/edit/<id>)
 └─ controllers → services/article_service.py::update
     ├─ MongoDB update_one        (DB gốc được cập nhật trước)
     └─ services/cache_service.py::invalidate_article(id)
          └─ DEL article:cache:<id>  +  DEL article:cache:hot:<id>  + xóa cache list
```

### Luồng C — Đăng nhập (Session Hash + TTL) — `services/session_service.py`

```
POST /login
 └─ controllers/auth_controller.py
     ├─ services/auth_service.py::authenticate  (so sánh password_hash)
     └─ services/session_service.py::create_session(user)
          ├─ session_id = token_hex(32)
          ├─ HSET session:<sid> user_id … user_agent
          ├─ EXPIRE session:<sid> 1800
          └─ Set-Cookie session_id=<sid> (HttpOnly, SameSite=Lax)

Mỗi request → before_request trong app.py:
     đọc cookie → EXISTS session:<sid>? → HGETALL → g.current_user → EXPIRE (gia hạn TTL)
```

---

## 7. Bảng "thầy hỏi → trả lời ở đâu"

| Câu hỏi của thầy | Trả lời ở đâu / nội dung cần nói |
|---|---|
| "Cache-Aside hoạt động thế nào?" | `services/cache_service.py` hàm `get_article()` — đọc Redis trước, miss thì đọc MongoDB rồi ghi ngược kèm TTL |
| "TTL đặt ở đâu, bao lâu?" | `config.py` (TTL_ARTICLE_CACHE=300, TTL_SESSION=1800) |
| "Sửa bài viết thì cache xử lý sao?" | `services/article_service.py::update` → `cache_service.invalidate_article()` (DEL key) |
| "Session lưu gì trên Redis?" | `services/session_service.py` — Hash `session:<sid>` + EXPIRE |
| "Mật khẩu lưu an toàn không?" | `models/user.py` / `services/auth_service.py` — `werkzeug.security.generate_password_hash` (scrypt) |
| "Lượt xem đếm bằng cách nào?" | `cache_service.incr_views()` → `INCR article:views:<id>` (atomic) |
| "Phân trang / lọc / sắp xếp ở đâu?" | `models/article.py::list_articles()` + index compound |
| "Ảnh bài viết lưu kiểu gì?" | `database/seed_articles.py` (sinh bằng Pillow) + `static/uploads/`; DB lưu đường dẫn |
| "Đo hiệu năng thế nào?" | `scripts/benchmark.py` + `scripts/plot_benchmark.py` |
| "Backup/Restore ra sao?" | `database/backup.py` / `database/restore.py` (kèm `mongodump`/`mongorestore`) |
| "Có test không?" | `tests/` — chạy `python -m pytest tests/ -v` (20 test) |
| "Bảo mật thế nào?" | Hash mật khẩu, cookie HttpOnly, biến môi trường trong `.env` không commit, escape regex khi tìm kiếm |

---

## 8. Cách chạy lại từ đầu

```bat
:: 1) Bật MongoDB (đã có sẵn service Windows) và Redis
scripts\start_redis.bat

:: 2) Tạo môi trường Python và cài thư viện
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

:: 3) Nạp dữ liệu mẫu
.venv\Scripts\python database\seed_articles.py --reset
.venv\Scripts\python database\seed_redis.py --reset

:: 4) Chạy ứng dụng
.venv\Scripts\python app.py      →  http://127.0.0.1:5000

:: 5) Kiểm thử
.venv\Scripts\python -m pytest tests/ -v

:: 6) Đo hiệu năng + vẽ biểu đồ
.venv\Scripts\python scripts\benchmark.py --n 200 --http http://127.0.0.1:5000
.venv\Scripts\python scripts\plot_benchmark.py
```

Tài khoản demo: `sv1_admin` / `sv2_editor` / `sv3_editor` — mật khẩu `123456`.
