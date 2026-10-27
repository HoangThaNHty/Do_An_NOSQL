# Kiểm thử Điểm Tin

## Chạy pytest

Cài `requirements.txt`; bật MongoDB và Redis như README. Từ gốc repo:

```powershell
.venv\Scripts\python -m pytest tests -q
```

`tests/conftest.py` đặt `REDIS_DB=13` trước khi các module test đọc config. Nếu cần DB khác, dùng `TEST_REDIS_DB` từ 1–15, dành riêng cho test; giá trị 0 bị từ chối. Cấu hình host/port/password vẫn từ môi trường hoặc `.env`.

```powershell
$env:TEST_REDIS_DB='14'
.venv\Scripts\python -m pytest tests -q
Remove-Item Env:TEST_REDIS_DB
```

Các test cache có thể xóa/reset key trong DB test. MongoDB dùng `nosql_news_test` và DB `nosql_news_flow_test_<uuid>`; fixture có drop DB test. Không đặt dữ liệu cần giữ vào các namespace này. Không chạy test với DB Redis đang dùng cho demo hay ứng dụng khác.

## Phạm vi

| File | Kiểm tra |
|---|---|
| `test_article.py` | CRUD/model/chỉ mục trên MongoDB test |
| `test_cache.py`, `test_cache_lock.py` | HIT/MISS, TTL, invalidation, counter, lease/token/timeout |
| `test_session.py` | Session Hash, TTL/gia hạn/đăng xuất |
| `test_user_flows.py` | Form/API, hai role, draft, cookie, đọc sau riêng theo người dùng |
| `test_search.py` | Không dấu, lỗi gõ, chủ đề và xếp hạng |
| `test_benchmark.py` | Payload, status/source và nguyên tắc đo |

Chỉ chạy nhóm không cần DB:

```powershell
.venv\Scripts\python -m pytest tests/test_search.py tests/test_benchmark.py -q
```

Mốc trước đóng gói: 71 pytest đạt. Xem [kết quả checkout sạch](RELEASE_CHECK.md) cho lần xác minh bản đưa lên GitHub.

## MCP Playwright

Các `tests/playwright_*.js` là hàm `async (page) => {...}` để truyền cho MCP Playwright `browser_run_code_unsafe`, không phải một bộ npm test độc lập. Cần app đã chạy; đa số script giả định `http://127.0.0.1:5000`, tài khoản seed cục bộ và dữ liệu mẫu. Kiểm tra script trước khi dùng trên DB có dữ liệu khác.

- `playwright_saved.js`: đăng ký/login, chuyển lại bài, lưu/bỏ lưu, mobile, hai tài khoản.
- `playwright_search*.js`: tìm kiếm/gợi ý, phản hồi cũ và bàn phím.
- `playwright_lock.js`: request cùng bài lạnh và thống kê khóa.
- `playwright_manage.js`: CRUD/quyền quản trị; có tạo dữ liệu thử.

Ảnh/log trình duyệt được giữ cục bộ, không phải tài nguyên chạy app. `docs/saved-qa-results.json` và `docs/lock-qa-results.json` ghi kết quả lịch sử; không coi đó là kết quả chạy lại ở máy mới. Các tài khoản tạm do test browser tạo cần được dọn đúng ID sau chạy; không xóa tài khoản ngoài phạm vi test.

## Benchmark không phải pytest

Chỉ đo khi app cùng DB/cấu hình, `SIMULATED_DB_LATENCY_MS=0`, cùng DTO và kiểm tra source. JSON/CSV hiện có là số đo ngày 26/10/2026. `--rtt` hoặc delay trong demo khóa là mô phỏng, không thay cho độ trễ thực. Xem [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md).
