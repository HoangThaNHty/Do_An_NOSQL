# Kết quả benchmark đã đo lại

Thời điểm: 2026-10-26T10:18:53.830511+07:00

Mỗi nguồn: 200 mẫu, 10 warm-up. p95: nearest-rank.

| Kịch bản | DB/MISS TB (ms) | Redis/HIT TB (ms) | DB/MISS p95 (ms) | Redis/HIT p95 (ms) | Tỷ số TB DB/Redis |
|---|---:|---:|---:|---:|---:|
| Nội dung một bài (DTO) | 0.709 | 0.519 | 1.359 | 1.008 | 1.36× |
| Danh sách 9 bài và phân trang | 2.769 | 0.752 | 4.341 | 1.396 | 3.68× |
| MÔ PHỎNG: MongoDB thêm 50 ms | 51.683 | 0.918 | 52.811 | 1.517 | 56.31× |
| HTTP: cache MISS / HIT | 12.889 | 8.554 | 31.340 | 27.993 | 1.51× |

Mô phỏng được ghi rõ từng dòng và vẽ riêng. HTTP gồm request + giải mã JSON; không đồng nhất với thời gian một lệnh Redis.

Không có dòng cache tìm kiếm: chức năng tìm kiếm gần đúng hiện không cache kết quả trong app.

Nguồn: data/result_benchmark.json và CSV cùng tên chứa các mẫu thô. Xem docs/PERFORMANCE_REPORT.md để biết phương pháp và giới hạn.
