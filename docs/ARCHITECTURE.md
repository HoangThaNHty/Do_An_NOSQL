# Kiến trúc hệ thống — Đề tài 06

Cập nhật 27/10/2026. Phiên bản hiện tại có hai quyền: Quản trị viên và Độc giả.

## Các tầng

| Tầng | Vị trí | Trách nhiệm |
|---|---|---|
| Giao diện | views/, static/ | Jinja2, Bootstrap 5, CSS và JavaScript cục bộ |
| Điều phối | controllers/ | Nhận request, kiểm tra quyền, gọi service, trả HTML/JSON |
| Nghiệp vụ | services/ | Cache-Aside, invalidation, xác thực, phiên và lượt xem |
| Dữ liệu | models/ | Truy vấn MongoDB, chỉ mục, chuyển đổi dữ liệu |
| Khởi tạo | app.py, config.py | Kết nối MongoDB/Redis, dependency injection, middleware |

MongoDB lưu users/articles. Redis lưu cache bài, cache danh sách, phiên đăng nhập, lượt xem, Hit/Miss và Set bài đọc sau. Không gọi Redis là nguồn lưu bền vững của nội dung bài.

## Luồng chính

Đọc bài: Controller → ArticleService → HGETALL Redis. Nếu miss, gọi MongoDB rồi HSET + EXPIRE. Trang chi tiết công khai chỉ trả bài đã xuất bản. GET trang HTML tăng lượt xem; GET API chỉ đọc không tăng.

Sửa/xóa: cập nhật MongoDB → xóa cache thường, cache hot và cache danh sách. Tạo mới cũng xóa cache danh sách. Bản nháp xuất hiện trong quản trị nhưng không xuất hiện ở trang đọc công khai.

Đăng nhập: kiểm tra mật khẩu băm scrypt → token ngẫu nhiên → HSET session → EXPIRE → cookie HttpOnly, SameSite=Lax. Mỗi request có phiên hợp lệ gia hạn cả Redis TTL lẫn thời hạn cookie. Đăng xuất xóa Hash và cookie.

Xem nhiều nhất: đọc lượt xem Redis theo lô, xếp hạng trước khi phân trang. Trang chủ, sidebar và danh sách dùng cùng cách tính. Không sắp theo views của MongoDB. Bộ đếm Redis hết hạn theo TTL nên không phải tổng lượt xem vĩnh viễn.

Bài liên quan: cùng chuyên mục, published, loại trừ bài đang đọc, tối đa ba bài.

## Key Redis

| Mẫu | Kiểu | TTL mặc định |
|---|---|---|
| article:cache:<id> | Hash | 300 giây |
| article:cache:hot:<id> | Hash | 1800 giây; chuẩn bị cho demo, luồng đọc thường dùng cache thường |
| article:list:v2:<page>:<per_page>:<sort>:<filters> | String JSON | 60 giây |
| article:views:<id> | String counter | 86400 giây, gia hạn mỗi lượt xem |
| session:<sid> | Hash | 1800 giây, gia hạn khi hoạt động |
| user:saved:<user_id> | Set | Không TTL; logout không xóa |
| lock:<cache-key> | String token | PX 10000 ms |
| meta:article-list-version | String counter | Không TTL |
| stats:cache:hits / stats:cache:misses / lock_waits / lock_timeouts | String counter | Không TTL |

## Quyền

Khách được đọc/tìm kiếm. Độc giả được thêm trang cá nhân, lưu/bỏ lưu bài đọc sau và đăng xuất. Chỉ Quản trị viên được CRUD bài, xem người dùng và theo dõi/thay đổi cache, xem các phiên khác. Đăng ký công khai luôn tạo Độc giả.

## Dữ liệu và chỉ mục

articles có tiêu đề, slug, tóm tắt, nội dung, ảnh, alt, chú thích ảnh, chuyên mục, tags, trạng thái, tác giả và thời gian. users có username/email duy nhất, password_hash, tên hiển thị, role, thời gian tạo/đăng nhập.

Chỉ mục articles: slug unique; category + created_at; author; created_at. Chỉ mục users: username/email unique và role. Tìm kiếm gần đúng chuẩn hóa dấu, so khớp từ và chấm điểm chủ đề bằng Python trên tập bài đã lọc; **không có text index hoặc vector search**.

100 bài kiến thức tiếng Việt được quản lý trong data/article_catalog.py, dùng 25 ảnh thuộc kho 30 ảnh mở đã có. Nguồn ảnh: static/images/CREDITS.md. Tài nguyên chạy offline.

Backup/restore dùng Extended JSON cho MongoDB và dữ liệu + TTL cho Redis, không phải mongodump/mongorestore. Các file sao lưu nằm trong data/exports/ và được gitignore.

Kiểm thử: [TESTING.md](TESTING.md). Cài đặt: [README.md](../README.md). Đóng góp: [CONTRIBUTING.md](CONTRIBUTING.md).

Gợi ý tìm kiếm: GET /api/articles/suggestions?q=, chỉ trả bài published, tối đa năm kết quả. UI hỗ trợ debounce, hủy request cũ và bàn phím. Khóa và benchmark đã có trong phiên bản hiện tại; xem PERFORMANCE_REPORT.md cho bằng chứng và giới hạn.

## Khóa nạp cache

Hash bài và String danh sách đều dùng khóa lock:<cache-key>. SET NX PX có lease10s; chờ tối đa khoảng2s, poll20ms. Lua xác nhận token khi ghi cache và nhả khóa; chủ mất lease không ghi đè hay xóa khóa của người khác. Danh sách dùng generation counter meta:article-list-version để chống publish bản cũ sau invalidation. Quá hạn chờ trả503 có Retry-After. Xem tests/test_cache_lock.py và docs/PERFORMANCE_REPORT.md.

Cache Hash bổ sung metadata slug/author/seed_version, giữ schema và kiểu giống API khi MISS. Test so sánh toàn bộ payload MISS/HIT.


## Đọc sau

SavedService dùng Set user:saved:<uid> riêng theo ID trong session. SADD/SREM/SISMEMBER/SMEMBERS; không TTL, không có thứ tự/thời điểm lưu. Lấy danh sách truy vấn MongoDB bằng $in và status=published, sort ngày đăng trước phân trang. Bài xóa/ẩn không hiện nhưng tham chiếu có thể còn. Set không có bản sao MongoDB; cần persistence/eviction/backup phù hợp nếu muốn giữ dữ liệu qua sự cố.
