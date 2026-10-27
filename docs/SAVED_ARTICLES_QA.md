# Điểm Tin — lưu bài để đọc sau

Cập nhật 26/10/2026. Đổi tên hiển thị, tiêu đề tab, đầu trang, chân trang và hai trang xác thực sang Điểm Tin. Khẩu hiệu: “Đọc thêm, hiểu hơn.” Nội dung đăng nhập/đăng ký giải thích lợi ích đọc sau; không hiển thị thông tin tài khoản mẫu hay thuật ngữ kỹ thuật.

## Cách sử dụng

1. Mở bài viết, chọn **Lưu để đọc sau**. Nếu chưa đăng nhập, đăng nhập rồi được đưa trở lại bài viết.
2. Chọn **Bài đã lưu** ngay cạnh nút lưu hoặc trong menu tài khoản.
3. Chọn **Bỏ lưu** trên bài viết hoặc trong danh sách.

Danh sách có phân trang, sắp xếp theo ngày đăng mới nhất, không theo thời điểm lưu. Bài chưa xuất bản hoặc đã xóa không hiện ra. Bài tạm chuyển sang nháp vẫn giữ tham chiếu và xuất hiện lại nếu được xuất bản lại.

## Thiết kế Redis Set

- Key: `user:saved:<MongoDB user_id>`, mỗi thành viên là ID bài viết.
- `SADD`: lưu, không sinh bản trùng; `SREM`: bỏ lưu; `SISMEMBER`: trạng thái nút; `SMEMBERS`: lấy ID để truy vấn bài công khai trong MongoDB bằng `$in`.
- Không đặt TTL (`TTL = -1`). Đăng xuất chỉ xóa session. Dữ liệu vẫn phụ thuộc cấu hình persistence, backup và chính sách eviction của Redis; không phải một bản sao trong MongoDB.
- API: `GET /api/saved?page=1&per_page=9`, `PUT /api/saved/<id>`, `DELETE /api/saved/<id>`; tất cả yêu cầu đăng nhập. Danh tính lấy từ session, không lấy từ payload.
- `GET /saved` là trang danh sách cá nhân. Không dùng bộ nhớ đệm danh sách công khai cho dữ liệu này.

Mã: `services/saved_service.py`, `controllers/saved_controller.py`, `views/saved_articles.html`, `static/js/saved.js`.

## Kết quả kiểm thử

- **71/71 pytest** đạt, MongoDB kiểm thử riêng và Redis DB 13. Bao gồm phân quyền, ID sai, bản nháp, lưu trùng, Set không TTL, cách ly tài khoản, lưu qua đăng xuất, gỡ bài và bỏ lưu lặp lại, chặn chuyển hướng đăng nhập ra ngoài.
- **19/19 kiểm tra MCP Playwright** đạt. Script tái chạy: `tests/playwright_saved.js`; kết quả: `docs/saved-qa-results.json`.
- Kiểm tra desktop 1440px và mobile 390px, đăng ký bằng form, đăng nhập trở về bài đang đọc, lưu/tải lại/bỏ lưu, trạng thái rỗng, hai phiên người dùng riêng biệt, không lỗi JavaScript.
- Phát hiện và sửa card cao 100% khiến nút bỏ lưu bị phân trang che trên mobile; lần chạy cuối bấm nút bình thường, không dùng force click.
- Ảnh/log giao diện được giữ cục bộ; không bắt buộc để clone và chạy source.

## Demo Redis Insight

Đăng nhập, lưu một bài, rồi lọc `user:saved:*` trong Redis Insight. Mở đúng key người dùng, chỉ ra kiểu **Set**, thành viên là ID bài và TTL không hết hạn. Lưu lại cùng bài không tăng số thành viên; bỏ lưu làm mất thành viên. Redis xóa key Set khi thành viên cuối cùng bị bỏ. Không sửa/xóa key của tài khoản khác để demo.
