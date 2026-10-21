# 📰 Tin Tức NoSQL — ĐỀ TÀI 06
## Phân hệ Caching bài viết & Quản lý phiên (Session Management)

Ứng dụng web tin tức trực tuyến xây dựng bằng **Flask + MongoDB + Redis**, hiện thực hóa
mẫu **Cache-Aside Pattern**, **Cache Invalidation**, quản lý **Session bằng Redis Hash**,
và bộ đếm lượt xem bằng lệnh **INCR**.

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript | Giao diện tin tức + trang quản trị |
| Backend | Python 3.13 + Flask 3.1 | REST API và xử lý nghiệp vụ |
| Database gốc | MongoDB 8 + PyMongo | Lưu `users`, `articles` (100 bài viết) |
| Cache / Session | Redis 8.10 + redis-py | Cache bài viết, TTL, Session Hash, bộ đếm lượt xem |
| GUI quan sát | MongoDB Compass, Redis Insight | Demo trực quan dữ liệu & TTL |
| Kiểm thử | pytest | 20 test cho CRUD / Cache / Session |
| Đo hiệu năng | script Python + matplotlib | Biểu đồ so sánh MongoDB vs Redis (Chương 8) |

---

## 1. Yêu cầu môi trường

| Phần mềm | Phiên bản | Ghi chú |
|---|---|---|
| Python | 3.13 | Kèm `pip install -r requirements.txt` |
| MongoDB | 8.x | Đang chạy sẵn ở `127.0.0.1:27017` (không authentication) |
| Redis | 8.10 | Bản Windows portable, đặt ở `D:\Redis` — chạy bằng `data\start_redis.bat` |
| MongoDB Compass | mới nhất | Xem & truy vấn DB gốc |
| Redis Insight | mới nhất | Xem key, Hash, TTL |
| Git | 2.54 | Quản lý mã nguồn theo 3 nhánh |

---

## 2. Cài đặt & chạy

```bat
:: (1) Bật MongoDB (service Windows) và Redis
data\start_redis.bat

:: (2) Tạo môi trường ảo Python + cài thư viện
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

:: (3) Tạo file cấu hình .env (copy từ .env.example)
copy .env.example .env

:: (4) Nạp dữ liệu mẫu: 100 bài viết + 100 ảnh + 50 key Redis có TTL khác nhau
.venv\Scripts\python database\seed_articles.py --reset
.venv\Scripts\python database\seed_redis.py --reset

:: (5) Chạy ứng dụng
.venv\Scripts\python app.py
```
👉 Mở trình duyệt: **http://127.0.0.1:5000**

**Tài khoản demo** (mật khẩu `123456`): `sv1_admin` · `sv2_editor` · `sv3_editor`

---

## 3. Các lệnh thường dùng

```bat
:: Kiểm thử (20 test)
.venv\Scripts\python -m pytest tests/ -v

:: Đo hiệu năng MongoDB vs Redis + vẽ biểu đồ
.venv\Scripts\python scripts\benchmark.py --n 200 --http http://127.0.0.1:5000
.venv\Scripts\python scripts\plot_benchmark.py

:: Backup / Restore
.venv\Scripts\python database\backup.py
.venv\Scripts\python database\restore.py --latest --drop

:: Bật/tắt mô phỏng độ trễ mạng khi demo (đọc DB gốc ~200ms)
data\toggle_latency.bat on
data\toggle_latency.bat off
```

---

## 4. Cấu trúc dự án (MVC)

```
app.py            config.py          requirements.txt
models/           -> MODEL          (dữ liệu, truy vấn MongoDB, index)
controllers/      -> CONTROLLER     (nhận request, gọi service, render view)
services/         -> BUSINESS LOGIC (Cache-Aside, TTL, Invalidation, INCR, Session Hash)
views/            -> VIEW           (Jinja2 template + partials dùng chung)
static/           -> CSS/JS/ảnh thật/font/vendor Bootstrap (không dùng CDN để demo offline)
data/             -> seed, fetch ảnh, backup, restore, benchmark, plot, .bat
tests/            -> pytest
docs/             -> ARCHITECTURE.md, DEMO_CHECKLIST.md, figures/, screenshots/
```

Chi tiết đầy đủ + bảng "thầy hỏi → trả lời ở đâu": **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)**

---

## 5. Các API chính

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `/` , `/articles` , `/articles/<id>` | Giao diện đọc bài (chi tiết dùng Cache-Aside) |
| GET | `/api/articles` | Danh sách bài viết (phân trang, lọc, sắp xếp) |
| GET | `/api/articles/search?q=` | Tìm kiếm nâng cao |
| GET | `/api/articles/<id>` | Chi tiết — response có `"source": "cache" \| "database"` |
| POST/PUT/DELETE | `/api/articles[/<id>]` | CRUD bài viết (sửa/xóa → tự xóa cache) |
| POST | `/api/auth/register` · `/login` · `/logout` | Đăng ký / đăng nhập / đăng xuất |
| GET | `/api/auth/session` | Thông tin phiên hiện tại + TTL còn lại |
| GET | `/api/cache/stats` · `/sessions` · `/keys` | Theo dõi trạng thái Redis (hỗ trợ demo) |
| POST | `/api/cache/invalidate/<id>` | Xóa cache một bài viết |
| GET | `/api/health` | Kiểm tra kết nối MongoDB + Redis |

---

## 6. Điểm nhấn kỹ thuật của đề tài

1. **Cache-Aside** — đọc Redis trước; Cache Hit trả ngay, Cache Miss mới đọc MongoDB rồi
   ghi ngược lại Redis kèm `EXPIRE`.
2. **Cache Invalidation** — sửa/xóa bài viết ⇒ xóa ngay key `article:cache:<id>`.
3. **Session bằng Redis Hash** — `HSET session:<sid> …` + `EXPIRE`, cookie `HttpOnly`,
   tự gia hạn TTL khi người dùng còn hoạt động (sliding expiration).
4. **Bộ đếm lượt xem bằng `INCR`** — thao tác nguyên tử, cập nhật thời gian thực.
5. **Bộ đếm Cache Hit/Miss** — `stats:cache:hits` / `stats:cache:misses` để chứng minh
   cache thực sự hoạt động (hiển thị ngay trên trang quản trị).
6. **Dummy data đúng định mức** — 100 bài viết có tiêu đề/nội dung/hình ảnh; 50 key Redis
   với TTL khác nhau (300s / 1800s / 60s / 1800s…).

---

## 7. Nhánh Git

| Nhánh | Phạm vi phụ trách |
|---|---|
| `main` | Bản tích hợp, ổn định để demo |
| `feature/database-article-crud` | MongoDB, model, CRUD bài viết, trang quản trị (SV1) |
| `feature/redis-cache` | Cache-Aside, TTL, Invalidation, INCR, giao diện đọc tin (SV2) |
| `feature/session-performance` | Auth, Session Redis, backup/restore, đo hiệu năng (SV3) |
