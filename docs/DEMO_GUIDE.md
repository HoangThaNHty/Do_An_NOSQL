# Demo Điểm Tin trên web, Compass và Redis Insight

Cài theo [README](../README.md). MongoDB/Redis có thể cài sẵn hoặc bật bằng `docker compose up -d --wait`; không phụ thuộc đường dẫn máy trưởng nhóm. GUI là công cụ quan sát, không bắt buộc để app chạy.

## Chuẩn bị

1. Nạp dữ liệu bằng `data/seed_articles.py` nếu DB mới; mở web và kiểm tra `/api/health`.
2. Compass dùng cùng `MONGO_URI` và `MONGO_DB_NAME` trong `.env`.
3. Redis Insight dùng cùng host/port/password và Redis DB index trong `.env`.
4. Tài khoản seed cục bộ mới tạo: admin hoặc reader, mật khẩu 123456.

Với Compose mặc định, MongoDB ở 127.0.0.1:27017 và Redis ở 127.0.0.1:6379, DB0. Không sao chép URI có mật khẩu của máy khác vào tài liệu.

## Bốn luồng nên chứng minh

| Luồng | Trên web | Trên GUI và điều cần nói |
|---|---|---|
| Cache-Aside | Admin vô hiệu hóa cache một bài; đọc API lần 1/lần 2 | Hash article:cache:<id> có TTL; source database rồi cache |
| Invalidation | Sửa bài trong quản trị, tải lại | MongoDB đổi, cache cũ bị xóa rồi nạp mới, không chờ TTL tự hết |
| Session | Login, tạm dừng request, logout | Hash session:<sid> có user_id/role/TTL; hoạt động gia hạn, logout xóa key |
| Đọc sau | Reader lưu, xem Bài đã lưu, lưu lặp, bỏ lưu | Set user:saved:<uid> chứa ID; không trùng/không TTL; key mất khi bỏ phần tử cuối |

Khách và reader không được gọi API quản trị; đăng ký công khai chỉ tạo reader. Khách chưa đăng nhập không phải role thứ ba.

## Những điểm cần nói chính xác

- Dừng tab thống kê admin tự lấy dữ liệu khi quan sát TTL phiên giảm.
- HTML chi tiết tăng views; API GET bài không tăng. Counter có TTL, không phải người xem duy nhất hoặc tổng vĩnh viễn.
- Tìm gần đúng dùng Python và nhóm chủ đề giới hạn, không gọi là AI.
- Khóa có lease/token; delay trong demo khóa chỉ để quan sát, không phải độ trễ MongoDB thật.
- seed_redis.py dùng khi cần key mẫu; session và thống kê giả lập không chứng minh hiệu năng.
- Restore và pytest dùng DB riêng; không --drop/flush DB demo.

Chi tiết thao tác/lời giải thích: [DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md). Số đo: [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md). Kiểm thử: [TESTING.md](TESTING.md).
