# Kiểm tra bản chuẩn bị đưa lên GitHub

Ngày 27/10/2026. Repo đích: https://github.com/HoangThaNHty/Do_An_NOSQL.

## Phạm vi và môi trường

Đã clone riêng từ nhánh chuẩn bị phát hành ở commit `e8bdbc4`, tạo `.venv` mới bằng Python 3.13, cài toàn bộ `requirements.txt` và chạy ứng dụng với MongoDB/Redis trên máy Windows. Các thay đổi sau mốc kiểm thử này chỉ bổ sung biên bản kiểm tra.

MongoDB dùng database có tên riêng cho lần kiểm tra; Redis dùng DB 15 cho HTTP và DB 12 cho pytest, đã kiểm tra trống trước khi chạy. Sau khi dừng server kiểm thử, dữ liệu tạm đã được dọn; database ứng dụng gốc vẫn có 100 bài và 6 tài khoản.

## Kết quả thực hiện ngày 27/10/2026

| Hạng mục | Kết quả |
|---|---|
| Checkout source | 146 file được theo dõi; không có `.env`, môi trường Python, log, backup hoặc bộ báo cáo Word/PDF/PPTX |
| Cài dependencies trong môi trường mới | Thành công; `pip check` không phát hiện dependency hỏng |
| Seed trên DB mới | 100 bài, 2 tài khoản mẫu; chạy lại không thêm bài hoặc tài khoản trùng |
| Bộ pytest từ clone sạch | **71 passed**, thời gian 7,15 giây |
| Kiểm tra HTTP trên server của clone sạch | **28/28 đạt** |
| Tài nguyên đi kèm | **61/61** file static tải qua HTTP thành công |
| Liên kết tài liệu và font CSS nội bộ | Không phát hiện đường dẫn thiếu trong checkout |

Các kiểm tra HTTP bao gồm trang chủ/đăng nhập/đăng ký/danh sách/chi tiết, health, gợi ý tìm kiếm, chặn truy cập trái quyền, đăng nhập hai role, lưu bài không trùng bằng Redis Set và giữ sau đăng xuất, bỏ lưu, quản trị, tạo/sửa/xóa bài, cache MISS/HIT cùng dữ liệu và nạp nội dung mới sau invalidation.

Đã rà các mẫu credential phổ biến trong lịch sử Git; không phát hiện mẫu khóa riêng, token GitHub, AWS hoặc URI MongoDB kèm mật khẩu trong phạm vi quét. Đây không phải chứng nhận kiểm toán bảo mật đầy đủ. `.env` không được theo dõi. Giấy phép MIT có sẵn trên remote và lịch sử remote được giữ lại; bổ sung giấy phép các thư viện/font phân phối kèm.

## Giới hạn và cách tái lập

- Compose được cung cấp như lựa chọn khởi động hai dịch vụ DB. Máy kiểm tra không có Docker, nên chưa xác minh chạy Compose; kết quả trên dùng MongoDB/Redis chạy trực tiếp.
- Lần này kiểm tra bằng pytest và HTTP, không chạy lại Playwright. Kết quả Playwright cũ trong tài liệu vẫn mang ngày kiểm tra riêng.
- File báo cáo, ảnh kiểm thử và script tạo báo cáo được giữ trên máy, loại khỏi checkout hiện tại. Lịch sử Git cũ được bảo toàn, nên các file từng commit vẫn có thể xuất hiện trong lịch sử.
- Xem [README](../README.md) để dựng môi trường và [TESTING](TESTING.md) để chạy test trên DB riêng. Không chạy test trên Redis DB dùng demo.

Log chi tiết và script kiểm tra tạm nằm trong `.artifacts/publish-audit/` trên máy thực hiện, được bỏ qua bởi Git; không phải thành phần cần thiết để chạy ứng dụng.
