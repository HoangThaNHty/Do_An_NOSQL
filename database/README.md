# Database mẫu nộp đồ án Nhóm 11

Đây là bộ dữ liệu MongoDB có thể khôi phục của **Điểm Tin**, đi kèm mã nguồn trong repo.
Gồm **100 bài tiếng Việt và 2 tài khoản demo**. Dữ liệu được tạo từ bộ bài mẫu của
project; không chứa tài khoản cá nhân, phiên đăng nhập hoặc bản sao dữ liệu riêng trên máy nhóm.

| File | Nội dung |
|---|---|
| `articles.json` | Collection bài viết, định dạng MongoDB Extended JSON |
| `users.json` | Hai tài khoản demo, mật khẩu lưu dạng băm scrypt |
| `import_database.py` | Nhập cả hai collection và tạo chỉ mục bằng model hiện tại |

## Khôi phục và chạy — Windows PowerShell

Sau khi clone repo, cài Python/thư viện và bật MongoDB + Redis theo README gốc,
chạy tại thư mục gốc project:

```powershell
.venv\Scripts\python database/import_database.py --database nosql_news
.venv\Scripts\python app.py
```

Trong `.env`, đặt `MONGO_DB_NAME=nosql_news`. Mở `http://127.0.0.1:5000`.
Chỉ nhập vào database rỗng; script từ chối nếu `articles` hoặc `users` đã có document.
Nếu máy đã có dữ liệu demo, có thể giữ nguyên để chạy hoặc chọn database rỗng khác:

```powershell
.venv\Scripts\python database/import_database.py --database nosql_news_nhom11
```

Sau đó đổi `.env` thành `MONGO_DB_NAME=nosql_news_nhom11` và khởi động lại app.
Không cần chạy `seed_articles.py` sau khi đã nhập thành công bộ này.

Tài khoản học tập cục bộ:

| Tên đăng nhập | Mật khẩu | Quyền |
|---|---|---|
| `admin` | `123456` | Quản trị viên |
| `reader` | `123456` | Độc giả |

Hai tài khoản này được tạo riêng cho bộ nộp; thay mật khẩu khi dùng ngoài môi trường demo.

## Xem bằng MongoDB Compass

Kết nối `mongodb://127.0.0.1:27017`, mở database đã chọn. Collection `articles`
có 100 document, `users` có 2 document; tab Indexes hiển thị các chỉ mục do model tạo.
Extended JSON giữ `_id` là ObjectId và trường thời gian là Date khi nhập bằng script.
Ảnh nằm trong `static/images/`, trường `image` trong document tham chiếu tới đường dẫn này.

## Redis trong bộ nộp

Không cần nhập dump Redis. Bắt đầu với Redis cục bộ dành riêng cho app:

1. Mở một bài: app tạo Hash `article:cache:<id>` và bộ đếm `article:views:<id>`.
2. Đăng nhập: app tạo Hash `session:<sid>`; không công bố token phiên trong repo.
3. Bấm lưu bài: app tạo Set `user:saved:<user_id>` chứa ID bài của tài khoản đó.
4. Mở Redis Insight để xem các key vừa được tạo.

Bộ nộp tạo lại trạng thái demo bằng các thao tác trên, không khôi phục lịch sử đọc,
lượt xem hoặc bài đã lưu của máy cũ. Cache là bản sao dựng lại từ MongoDB; phiên
và bài đã lưu là trạng thái Redis riêng, không có trong hai file MongoDB.

Nguồn dữ liệu: `data/article_catalog.py`. Chỉ mục và schema thao tác:
`models/article.py`, `models/user.py`. Bản này là dữ liệu mẫu có thể chạy lại,
không phải bản sao lưu toàn bộ môi trường đang chạy của nhóm.
