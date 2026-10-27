# Khóa Redis và kết quả đo lại hiệu năng

Thời điểm: 2026-10-26T10:18:53.830511+07:00

## Kết quả thực tế cục bộ

| Kịch bản | DB/MISS TB | Redis/HIT TB | DB/MISS p95 | Redis/HIT p95 | Tỷ số TB |
|---|---:|---:|---:|---:|---:|
| Nội dung một bài (DTO) | 0.709 ms | 0.519 ms | 1.359 ms | 1.008 ms | 1.36× |
| Danh sách 9 bài và phân trang | 2.769 ms | 0.752 ms | 4.341 ms | 1.396 ms | 3.68× |
| HTTP: cache MISS / HIT | 12.889 ms | 8.554 ms | 31.340 ms | 27.993 ms | 1.51× |

Mỗi nguồn có 200 mẫu sau 10 warm-up, đảo thứ tự mỗi vòng. Các kết quả này thay thế số benchmark cũ, không phải cam kết SLA.

## Môi trường

Windows-11-10.0.26300-SP0; Python 3.13.13; Flask 3.1.3; MongoDB 8.3.2; Redis 8.10.2; PyMongo 4.19.0; redis-py 8.1.0. Có 100 bài trong DB, cùng máy cục bộ. HTTP kiểm tra simulated_db_latency_ms=0 từ health endpoint.

## Phương pháp đã sửa

- Hai nguồn trả cùng DTO; xác nhận ở từng mẫu sau khi dừng đồng hồ.
- Đảo thứ tự đo mỗi vòng; warm-up riêng; lưu mọi mẫu thô và p95 nearest-rank.
- Chuẩn bị/xóa cache nằm ngoài vùng bấm giờ; HTTP kiểm tra status và source.
- Lớp dữ liệu đo đọc + chuyển đổi; HTTP đo trọn request và giải mã JSON.
- Mô phỏng được ghi thành kịch bản riêng; không suy ra thời gian Redis từ tổng HTTP.
- Tìm kiếm hiện không cache trong app nên không đưa cache tìm kiếm giả định vào bảng.
- MongoDB chuyển kiểu và chiếu trường trực tiếp, không phải encode rồi decode JSON thừa để tạo DTO. Redis giải mã đúng dạng đã lưu.
- Hash nội dung bài chứa cùng schema/kiểu với dữ liệu API (kể cả tác giả, slug, seed_version); có test đảm bảo MISS/HIT trả cùng payload.
- Payload chi tiết không gồm bộ đếm lượt xem; danh sách là 9 DTO cộng metadata phân trang. HTTP đọc bài dùng views hiện tại của app và so toàn bộ data.
- Cache dữ liệu dùng namespace benchmark:<uuid> và được dọn sau lần chạy. HTTP chỉ làm lạnh cache của bài được chọn, không xóa session/counter hay toàn Redis DB.
- CSV chứa đúng từng mẫu được đo; warm-up và yêu cầu chuẩn bị không có trong CSV. Hit/Miss hiển thị trên app vẫn tính cả các yêu cầu warm-up/chuẩn bị vì chúng là request thật.

| Payload | Số byte JSON UTF-8 chuẩn hóa | Tương đương từng mẫu |
|---|---:|---|
| Nội dung một bài (DTO) | 2756 | Có |
| Danh sách 9 bài và phân trang | 24508 | Có |
| HTTP: cache MISS / HIT | 2768 | Có |

## Mô phỏng được tách riêng

MÔ PHỎNG: MongoDB thêm 50 ms: 51.683 ms so với 0.918 ms. Đây là thêm sleep 50 ms vào đường DB, không phải RTT đã đo từ một máy chủ mạng. Biểu đồ mô phỏng nằm riêng và không dùng để khẳng định mức tăng tốc thực tế.

## Cơ chế khóa đã bổ sung

- Khóa mỗi key: lock:<cache-key>; SET NX PX, token ngẫu nhiên; mặc định lease 10.000 ms, chờ tối đa khoảng 2.000 ms, thăm lại mỗi 20 ms. Cấu hình qua CACHE_LOCK_TTL_MS, CACHE_LOCK_WAIT_MS, CACHE_LOCK_POLL_MS.
- Một chủ giành khóa, kiểm tra cache lại rồi mới gọi loader. Các yêu cầu khác chờ cache, không tự bỏ qua khóa để truy vấn DB khi hết thời gian.
- Ghi cache và nhả khóa bằng Lua, kiểm tra token trong cùng thao tác. Chủ đã hết lease không ghi đè dữ liệu của chủ mới và không xóa khóa người khác.
- Lỗi loader hoặc không tìm thấy bài vẫn nhả khóa. Khi chủ chết, PX cho phép yêu cầu khác tiếp tục sau khi lease hết.
- Invalidation bài thu hồi khóa đang nạp. Danh sách có generation counter; thay đổi trong lúc loader chạy ngăn bản cũ được cache trở lại.
- Quá thời gian chờ trả HTTP 503 + Retry-After: 1; giao diện có trang thử lại. Một lượt phục vụ cache tính Hit, một lượt gọi loader tính Miss; chờ khóa/quá hạn có bộ đếm riêng.
- Lease có hạn, không tự gia hạn. Nếu loader chạy lâu hơn lease, có thể có lần nạp thay thế; token bảo vệ việc ghi cache, không bảo đảm mọi request chỉ nạp đúng một lần trong mọi sự cố. Cần đặt lease phù hợp timeout DB.
- Request đã đọc dữ liệu trước lúc có chỉnh sửa có thể vẫn trả bản đó cho chính request đang bay; cơ chế này ngăn ghi lại cache cũ, không hứa nhất quán tuyến tính cho toàn bộ DB và cache.

## Kiểm thử

65 test pytest đạt: các test cũ cùng test khóa đồng thời, lease, timeout, nhả đúng chủ, invalidation đang nạp, 503, DTO và nguyên tắc đo benchmark.

Demo CLI: 12 yêu cầu, 1 loader MongoDB, 11 cache, 11 lượt chờ, 0 timeout; khóa tự nhả. Delay 1000ms chỉ để quan sát, không phải benchmark MongoDB. Nguồn: data/result_lock_demo.json.

MCP Playwright: 12 HTTP request thật cùng bài lạnh, 1 source=database + 11 source=cache, payload giống nhau, số Miss tăng đúng 1; kiểm tra hai thống kê khóa trên UI và bố cục điện thoại. Trong lần này chỉ 2 request phải chờ, các request còn lại đến khi cache đã có. Có 5/5 kiểm tra đạt.

## Chạy lại

```powershell
.venv\Scripts\python -m pytest tests -q
.venv\Scripts\python data/benchmark.py --n 200 --warmup 10 --http http://127.0.0.1:5000 --rtt 50
.venv\Scripts\python data/plot_benchmark.py
.venv\Scripts\python data/demo_lock.py --workers 12 --delay-ms 1000
```

Test cache/session cũ dùng Redis DB cấu hình; chạy pytest trên DB riêng đang trống nếu muốn giữ thống kê demo (đợt này dùng DB13). Benchmark HTTP cần app cùng DB và phiên bản mới; nếu tắt/bật mô phỏng phải nạp lại app.

## File kết quả

- data/result_benchmark.json: môi trường, stats, tất cả mẫu thô và phương pháp.
- data/result_benchmark.csv: dữ liệu từng mẫu để đối chiếu.
- docs/figures/bang_so_sanh.md: bảng TB/p95.
- docs/figures/bieu_do_hieu_nang.png: số đo thật; thang dữ liệu và HTTP riêng.
- docs/figures/bieu_do_phan_bo.png: boxplot, giữ điểm ngoại lệ.
- docs/figures/bieu_do_mo_phong.png: chỉ mô phỏng.

Tài liệu này giữ kết quả ngày đo 26/10/2026. Hướng dẫn chạy hiện tại ở README.md và TESTING.md; sản phẩm Word/slide được quản lý riêng ngoài source.
