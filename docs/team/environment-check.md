# Công cụ Kiểm tra Môi trường (Environment Check)

Module được thiết kế nhằm giúp các thành viên trong dự án dễ dàng thẩm định môi trường lập trình của bản thân trước khi chạy code (tránh crash do sai cấu hình, thiếu thư viện).

## Tệp tin liên quan
- **Công cụ:** `data/check_env.py`
- **Unit test:** `tests/test_check_env.py`

## Hướng dẫn sử dụng

Yêu cầu kích hoạt virtual environment (`.venv`) trước khi thực thi.

### 1. Nghiệm thu Offline
Chạy lệnh bên dưới để công cụ đọc file `requirements.txt` và quét toàn bộ hệ thống xem bạn đã cài đặt đủ package chưa. Quá trình này **không** yêu cầu kết nối mạng hay bật Database.

```bash
python data/check_env.py --offline