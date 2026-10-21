# CHECKLIST DEMO SỐNG — ĐỀ TÀI 06
*(theo đúng kịch bản bảo vệ trong đề tài)*

> **Trước khi demo (5 phút):**
> 1. Mở MongoDB Compass → kết nối `mongodb://127.0.0.1:27017` → DB `nosql_news`
> 2. Mở Redis Insight → kết nối `127.0.0.1:6379` → Database `0`
> 3. Chạy `scripts\start_redis.bat` (nếu Redis chưa chạy)
> 4. Chạy `.venv\Scripts\python app.py`
> 5. Chạy `data\toggle_latency.bat on` → **khởi động lại app.py** (để thấy đúng
>    kịch bản "đọc DB gốc ~200ms")
> 6. `.venv\Scripts\python database\seed_redis.py --reset` (làm mới 50 key TTL khác nhau)

---

## BƯỚC 1 — SV3: Mở tab Network (F12), tải bài viết lần 1 vs lần 2

| | Thao tác | Kết quả mong đợi |
|---|---|---|
| 1.1 | F12 → tab **Network** → chọn `Fetch/XHR` | Khung hiển thị request |
| 1.2 | Mở `http://127.0.0.1:5000/articles/<id bất kỳ>` | Request **lần 1**: `Time ≈ 200ms+` |
| 1.3 | **F5 lại trang** | Request **lần 2**: `Time ≈ 5–15ms` |
| 1.4 | Xem tab **Response** của API `GET /api/articles/<id>` | Lần 1: `"source": "database"` → lần 2: `"source": "cache"` |
| 1.5 | Mở thêm tab `/admin/cache` (quản trị) | Bảng điều khiển: Cache Hit / Cache Miss tăng dần, cột TTL đếm lùi |
| 1.6 | Nói rõ: *"Lần 1 Cache Miss → đọc MongoDB; lần 2 Cache Hit → đọc Redis"* |

**Mẹo:** dùng `Ctrl+Shift+R` (hard reload) để chắc chắn không dính cache trình duyệt.

---

## BƯỚC 2 — SV1: Sửa nội dung bài viết

| | Thao tác | Kết quả mong đợi |
|---|---|---|
| 2.1 | Đăng nhập `sv1_admin` / `123456` | Navbar hiện tên + mục **Quản trị** |
| 2.2 | Vào `/admin/articles` → bấm **Sửa** ở một bài | Mở form sửa bài viết |
| 2.3 | Sửa tiêu đề / nội dung → **Lưu thay đổi** | Thông báo *"Đã cập nhật bài viết và xóa cache cũ (Cache Invalidation)"* |

---

## BƯỚC 3 — SV2: Chứng minh cache cũ bị xóa ngay lập tức

| | Thao tác | Kết quả mong đợi |
|---|---|---|
| 3.1 | Trước khi sửa: mở `/admin/cache` → tìm key `article:cache:<id>` (hoặc Redis Insight) | Có key, cột **TTL** đếm lùi |
| 3.2 | Sau khi SV1 bấm **Lưu**: refresh lại Redis Insight | **Key đã biến mất** (DEL) |
| 3.3 | Mở lại bài viết vừa sửa | Hiện **nội dung mới**, Response lại là `"source": "database"` (Cache Miss) |
| 3.4 | Mở lại lần nữa | `"source": "cache"` (Cache Hit) — key đã được tạo lại với TTL 300s |

> Nói rõ: *"Xóa cache theo cơ chế **Cache Invalidation** — cập nhật DB gốc trước, sau đó
> xóa key cache để lần đọc kế tiếp lấy dữ liệu mới. Đây là lý do không dùng
> Write-Through cho bài viết."*

---

## BƯỚC 4 — SV2: Bộ đếm lượt xem bằng INCR

| | Thao tác | Kết quả mong đợi |
|---|---|---|
| 4.1 | Ghi nhớ giá trị `article:views:<id>` trong Redis Insight | Ví dụ `128` |
| 4.2 | Mở bài viết đó 3–5 lần (F5) | Mỗi lần tăng đúng 1 |
| 4.3 | Quay lại Redis Insight | `128 → 131 …` (tăng thời gian thực) |
| 4.4 | Giải thích | *"Dùng lệnh `INCR` — thao tác nguyên tử (atomic), an toàn khi nhiều người xem cùng lúc"* |

---

## BƯỚC 5 — SV3: Redis Insight — Session Hash và TTL đếm lùi

| | Thao tác | Kết quả mong đợi |
|---|---|---|
| 5.1 | Redis Insight → tab **Browser** → lọc `session:*` | Thấy các key `session:<64 ký tự hex>` |
| 5.2 | Bấm vào 1 key | Hiện **Hash** với field: `user_id`, `username`, `email`, `role`, `login_at`, `ip`, `user_agent` |
| 5.3 | Nhìn cột **TTL** | Đếm lùi 1799 → 1798 → 1797 (thời gian sống còn lại) |
| 5.4 | Đăng nhập lại bằng `sv2_editor` | Key session mới xuất hiện với TTL 1800 |

---

## BƯỚC 6 — SV3: Logout → session bị xóa khỏi Redis

| | Thao tác | Kết quả mong đợi |
|---|---|---|
| 6.1 | Bấm **Đăng xuất** trên navbar | Quay về trang chủ, navbar mất tên người dùng |
| 6.2 | Redis Insight → lọc `session:*` | Key session vừa xóa **không còn** |
| 6.3 | Thử truy cập `/admin` | Bị chuyển về trang đăng nhập (middleware `login_required`) |

---

## BƯỚC 7 — SV3: Backup / Restore

| | Thao tác | Kết quả mong đợi |
|---|---|---|
| 7.1 | `.venv\Scripts\python database\backup.py` | Tạo `data/exports/backup_<timestamp>/` gồm `mongo_users.json`, `mongo_articles.json`, `redis_keys.json` |
| 7.2 | Xóa thử 1 bài viết trong `/admin/articles` | Bài biến mất |
| 7.3 | `.venv\Scripts\python database\restore.py --latest --drop` | Bài viết **quay lại** đầy đủ, Redis key cũng được khôi phục kèm TTL |

---

## BƯỚC 8 — SV3: So sánh hiệu năng (F12 / biểu đồ)

| | Thao tác | Kết quả mong đợi |
|---|---|---|
| 8.1 | Mở `docs/figures/bieu_do_hieu_nang.png` | Biểu đồ cột: MongoDB vs Redis cho 3–4 kịch bản |
| 8.2 | Chỉ vào bảng `docs/figures/bang_so_sanh.md` | Số liệu cụ thể (MongoDB ms vs Redis ms, nhanh hơn x lần) |
| 8.3 | Kết luận | *"Redis giảm thời gian phản hồi từ X ms xuống còn Y ms; khi MongoDB nằm ở máy khác (có độ trễ mạng ~50–200ms) chênh lệch còn lớn hơn nữa"* |

---

## PHỤ LỤC — Các lệnh dùng tay (để GV yêu cầu gõ lệnh Redis)

```bat
D:\Redis\redis-cli.exe PING
D:\Redis\redis-cli.exe KEYS "article:*"
D:\Redis\redis-cli.exe TYPE article:cache:<id>          :: hash
D:\Redis\redis-cli.exe HGETALL article:cache:<id>
D:\Redis\redis-cli.exe TTL article:cache:<id>            :: 300
D:\Redis\redis-cli.exe GET article:views:<id>            :: so luot xem
D:\Redis\redis-cli.exe INCR article:views:<id>           :: tang luot xem
D:\Redis\redis-cli.exe HGETALL session:<sid>
D:\Redis\redis-cli.exe TTL session:<sid>                 :: dem lui
D:\Redis\redis-cli.exe DEL article:cache:<id>            :: cache invalidation
D:\Redis\redis-cli.exe DBSIZE                            :: so key dang luu
D:\Redis\redis-cli.exe INFO memory
```

```bat
:: MongoDB (qua Python vì may chua cai mongosh)
.venv\Scripts\python -c "from pymongo import MongoClient; print(MongoClient('mongodb://127.0.0.1:27017')['nosql_news']['articles'].count_documents({}))"
```

---

## Checklist trước giờ trình bày

- [ ] MongoDB Compass mở được DB `nosql_news`, thấy 100 bài viết
- [ ] Redis Insight kết nối được, thấy ~50 key
- [ ] `app.py` chạy, trang chủ hiện 9 bài viết có ảnh
- [ ] Đăng nhập được bằng `sv1_admin` / `123456`
- [ ] `data\toggle_latency.bat on` đã bật + app.py đã restart
- [ ] Tab Network F12 đã mở sẵn, đã chọn filter **Fetch/XHR**
- [ ] Ảnh chụp màn hình lưu vào `docs/screenshots/`
