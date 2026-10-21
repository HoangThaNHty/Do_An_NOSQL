# HƯỚNG DẪN CHẠY DEMO — ĐỀ TÀI 06
## Trình diễn trực quan MongoDB (DB gốc) + Redis (Cache & Session)

> In bản này ra, làm theo từng bước khi trình bày. Thứ tự bên dưới là thứ tự **an toàn nhất** (không bao giờ để app báo lỗi giữa chừng).

---

## PHẦN 0 — CHUẨN BỊ (làm trước khi vào phòng thi, 5 phút)

### 0.1. Bật MongoDB (đã cài sẵn, chạy như Windows Service)

```powershell
Get-Service MongoDB          # kiểm tra trạng thái: Running = OK
Start-Service MongoDB        # nếu Stopped
```
MongoDB nghe ở `127.0.0.1:27017`, không có authentication. Dữ liệu nằm ở `D:\data`.

### 0.2. Bật Redis (đã cài ở `D:\Redis`, tự chạy khi mở máy)

```powershell
D:\Redis\redis-cli.exe ping          # phải trả về PONG
```
Nếu không có `PONG` → chạy `data\start_redis.bat` (hoặc mở `D:\Redis\redis-server.exe redis.conf`).

### 0.3. Nạp dữ liệu mẫu (để số liệu luôn đẹp khi demo)

```powershell
.venv\Scripts\python data\seed_articles.py --reset   # 100 bài viết + 100 ảnh
.venv\Scripts\python data\seed_redis.py --reset      # 47 key Redis với TTL khác nhau
```

### 0.4. Chạy ứng dụng

```powershell
.venv\Scripts\python app.py
```
→ Mở trình duyệt: **http://127.0.0.1:5000**

### 0.5. Mở sẵn 4 cửa sổ trước khi trình bày

| Cửa sổ | Dùng để làm gì |
|---|---|
| **Chrome** — tab `http://127.0.0.1:5000` | Demo ứng dụng |
| **Chrome** — tab `http://127.0.0.1:5000/admin/cache` | Bảng điều khiển Cache & Session (bằng chứng cho GV) |
| **MongoDB Compass** | Chứng minh dữ liệu nằm trong DB gốc |
| **Redis Insight** | Chứng minh Cache/Session nằm trên Redis + TTL đếm lùi |

### 0.6. (Tùy chọn) Bật mô phỏng độ trễ mạng để khớp kịch bản đề tài

```powershell
data\toggle_latency.bat on     # đọc DB gốc sẽ chậm ~200ms (như DB nằm ở máy khác)
# -> KHỞI ĐỘNG LẠI app.py để áp dụng
```
Khi demo xong: `data\toggle_latency.bat off` → restart app.

---

## PHẦN 1 — MỞ MONGO DB COMPASS (giáo viên muốn thấy DB gốc)

### 1.1. Kết nối

- Mở **MongoDB Compass**
- Dán vào ô connection string: `mongodb://127.0.0.1:27017` → **Connect**
- Chọn database **nosql_news** → thấy 2 collection: `users`, `articles`

### 1.2. Trình diễn truy vấn (mục 7 của thang điểm: "truy vấn cơ bản & nâng cao trên GUI Tool")

Trong tab **Collections → articles → Filters**, gõ:

| Mục đích | Bộ lọc / câu lệnh | Kết quả |
|---|---|---|
| Truy vấn cơ bản | `{ "status": "published" }` | 100 bài |
| Lọc theo chuyên mục | `{ "category": "Cong nghe" }` | 17 bài |
| Tìm kiếm | `{ "title": { "$regex": "AI", "$options": "i" } }` | các bài có "AI" |
| Sắp xếp | tab **Sort** → `created_at` desc | mới nhất lên đầu |
| Phân trang | tab **Limit/Skip** → limit 9, skip 0 | trang 1 |
| Tìm kiếm toàn văn | tab **Index** → text index trên `title` | tìm nhanh |

Trong **mongosh / Explain Plan** (nếu GV hỏi): index đã tạo gồm
`slug (unique)`, `category + created_at (compound)`, `author`, `created_at`, `title (text)`.

### 1.3. Chứng minh "bài viết hoàn chỉnh có tiêu đề, nội dung và hình ảnh"

Bấm vào 1 document → hiện đủ field: `title`, `summary`, `content`, `image` (`/static/images/news_001.jpg`), `category`, `tags`, `views`, `created_at`.
> Nói: *"Hình ảnh lưu dạng đường dẫn trong `static/images/`, tải từ Openverse theo giấy phép CC0/PDM — danh sách uy quyền nằm ở `static/images/CREDITS.md`."*

---

## PHẦN 2 — MỞ REDIS INSIGHT (giáo viên muốn thấy Cache & Session)

### 2.1. Kết nối

- Mở **Redis Insight**
- Chọn **Add Redis Database** → host `127.0.0.1`, port `6379`, username trống, password trống → **Add**
- Chọn database **DB 0** → tab **Browser**

### 2.2. Những gì cần chỉ ra (đúng theo yêu cầu đề tài)

| Tìm key | Kiểu dữ liệu | TTL hiển thị | Nói gì |
|---|---|---|---|
| `session:<64 ký tự hex>` | **Hash** | 1800 → 1799 → 1798… | *"Session lưu bằng Hash, TTL tự đếm lùi"* |
| `article:cache:<id>` | **Hash** | 300 | *"Cache bài viết, hết hạn sau 5 phút"* |
| `article:cache:hot:<id>` | **Hash** | 1800 | *"Bài nóng giữ cache 30 phút"* |
| `article:list:<page>:<sort>` | **String** | 60 | *"Cache danh sách 1 phút"* |
| `article:views:<id>` | **String** | 86400 | *"Bộ đếm lượt xem, tăng bằng INCR"* |
| `stats:cache:hits` / `:misses` | String | — | *"Đếm số lần Cache Hit / Miss"* |

> Bấm vào 1 key `session:...` → hiện các **field** bên trong Hash:
> `user_id`, `username`, `email`, `role`, `login_at`, `ip`, `user_agent`.

### 2.3. Nếu GV yêu cầu gõ lệnh trực tiếp (mở cmd)

```bat
D:\Redis\redis-cli.exe PING
D:\Redis\redis-cli.exe DBSIZE
D:\Redis\redis-cli.exe KEYS "article:*"
D:\Redis\redis-cli.exe TYPE article:cache:<id>          → hash
D:\Redis\redis-cli.exe HGETALL article:cache:<id>
D:\Redis\redis-cli.exe TTL article:cache:<id>            → 300
D:\Redis\redis-cli.exe GET article:views:<id>            → số lượt xem
D:\Redis\redis-cli.exe INCR article:views:<id>           → +1
D:\Redis\redis-cli.exe HGETALL session:<sid>
D:\Redis\redis-cli.exe TTL session:<sid>                 → đếm lùi
D:\Redis\redis-cli.exe DEL article:cache:<id>            → xóa cache (invalidation)
D:\Redis\redis-cli.exe INFO memory
```

---

## PHẦN 3 — TÀI KHOẢN & PHÂN QUYỀN 3 ROLE

Mật khẩu chung: `123456`

| Tài khoản | Email | Role | Được làm gì |
|---|---|---|---|
| `admin` | admin@uit.edu.vn | **admin** | Toàn quyền: quản lý bài viết, xem danh sách người dùng, xem bảng điều khiển Cache |
| `editor` | editor@uit.edu.vn | **editor** | Quản lý **nội dung** (thêm/sửa/xóa bài), xem bảng cache — **không** xem danh sách người dùng |
| `reader` | reader@uit.edu.vn | **reader** | Chỉ đọc tin tức, đăng nhập/đăng xuất — **không** vào được trang quản trị, API ghi trả về **403** |
| `sv1_admin` | sv1@uit.edu.vn | admin | Tài khoản của SV1 trong nhóm |
| `sv2_editor` | sv2@uit.edu.vn | editor | Tài khoản của SV2 trong nhóm |
| `sv3_editor` | sv3@uit.edu.vn | editor | Tài khoản của SV3 trong nhóm |

### 3.1. Tự kiểm tra bảng phân quyền trước khi demo

```powershell
.venv\Scripts\python data\check_roles.py
```
Kết quả mong đợi (9/9 OK):

```
Chuc nang                      admin    editor    reader
Doc trang chu                    200       200       200
Doc danh sach bai viet           200       200       200
Vao trang quan tri               200       200       302   (reader bi day ra)
Quan ly bai viet                 200       200       302
Danh sach nguoi dung             200       302       302   (chi admin)
Bang dieu khien cache            200       200       302
Tao bai viet qua API             201       201       403   (reader khong du quyen)
```

### 3.2. Trình diễn phân quyền trên giao diện (2 phút)

1. Đăng nhập `admin` → navbar hiện badge **admin** → vào `/admin/users` → thấy danh sách 6 user
2. Đăng xuất → đăng nhập `editor` → badge **editor** → vào `/admin/users` → **bị báo "Chỉ quản trị viên mới có quyền này"** và đẩy về dashboard
3. Đăng xuất → đăng nhập `reader` → badge **reader** → bấm thẳng URL `/admin/` → **bị đẩy về trang chủ** kèm thông báo "Bạn không có quyền truy cập trang này"

> Nói: *"Phân quyền thực hiện bằng decorator `@admin_required`, `@admin_only_required`, `@editor_required` trong `controllers/__init__.py`. Session lưu role trong Redis Hash nên quyền được kiểm tra mỗi request."*

---

## PHẦN 4 — KỊCH BẢN DEMO CHÍNH (chi tiết ở `DEMO_CHECKLIST.md`)

| Bước | Ai làm | Thao tác | Bằng chứng |
|---|---|---|---|
| 1 | SV3 | F12 → Network → mở bài viết (lần 1) | `~200ms`, Response `"source": "database"` |
| 2 | SV3 | F5 lại (lần 2) | `~10ms`, Response `"source": "cache"` |
| 3 | SV1 | Sửa bài viết trong `/admin/articles` | Thông báo *"… và xóa cache cũ (Cache Invalidation)"* |
| 4 | SV2 | Refresh Redis Insight | Key `article:cache:<id>` **biến mất** |
| 5 | SV2 | Mở lại bài vừa sửa | Hiện nội dung **mới**, `"source": "database"` (lần 2 sẽ hit lại) |
| 6 | SV2 | Mở bài nhiều lần | `article:views:<id>` tăng dần (INCR) |
| 7 | SV3 | Redis Insight + `/admin/cache` | Session Hash + TTL đếm lùi 1800→1799 |
| 8 | SV3 | Logout rồi vào lại Redis Insight | Key `session:*` đã bị xóa |
| 9 | SV3 | `data/backup.py` → xóa 1 bài → `data/restore.py --latest --drop` | Bài quay lại đầy đủ |

---

## PHẦN 5 — XỬ LÝ SỰ CỐ NHANH

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `/api/health` báo `"mongo": "error"` | MongoDB chưa chạy | `Start-Service MongoDB` |
| `/api/health` báo `"redis": "error"` | Redis chưa chạy | `data\start_redis.bat` → `redis-cli ping` phải ra `PONG` |
| Trang báo "Không tìm thấy bài viết" | Đã xóa nhầm dữ liệu | `python data\seed_articles.py --reset` |
| Bài viết hiển thị 0 lượt xem | Key `article:views:*` đã hết TTL | `python data\seed_redis.py --reset` |
| Cổng 5000 bị chiếm | Chạy 2 instance Flask | Đóng cửa sổ cũ, chạy lại `app.py` |
| Font chữ hiển thị lỗi | Thiếu file font | Kiểm tra `static\fonts\` có 16 file `.woff2` |
| Ảnh không hiện | Đường dẫn cũ `/static/uploads/` | Chạy lại `data\seed_articles.py --reset` |

---

## PHẦN 6 — CÂU HỎI GV HỎI & TRẢ LỜI Ở ĐÂU

| GV hỏi | Trả lời ở |
|---|---|
| Cache-Aside hoạt động thế nào? | `services/cache_service.py` → `get_article()` |
| TTL đặt ở đâu? | `config.py` (`TTL_ARTICLE_CACHE=300`, `TTL_SESSION=1800`) |
| Sửa bài thì cache xử lý sao? | `services/article_service.py` → `invalidate_article()` |
| Session lưu gì? | `services/session_service.py` → `HSET session:<sid>` + `EXPIRE` |
| Mật khẩu an toàn không? | `models/user.py` → `werkzeug.generate_password_hash` (scrypt) |
| Lượt xem đếm thế nào? | `cache_service.incr_views()` → `INCR` |
| Phân quyền ở đâu? | `controllers/__init__.py` (3 decorator) |
| Backup/Restore thế nào? | `data/backup.py` + `data/restore.py` (+ `mongodump`) |
| Đo hiệu năng ra sao? | `data/benchmark.py` + `data/plot_benchmark.py` → `docs/figures/` |
| Có test không? | `tests/` — `python -m pytest tests/ -v` (20 test) |

Chi tiết đầy đủ: **`docs/ARCHITECTURE.md`**
