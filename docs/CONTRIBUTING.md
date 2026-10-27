# Làm việc nhóm và Pull Request

Bản nền hiện có hai role, Cache-Aside/khóa, session và Redis Set đọc sau. Các thành viên bắt đầu từ `origin/main` mới, không tiếp tục nhánh feature cũ ở commit khởi tạo. Nhánh riêng và PR ghi nhận thay đổi mới thực sự làm; không tự suy ra tác giả của các module cũ.

## Ba mảng bổ sung dự kiến

| Mã | Nhánh | File được thêm | Tiêu chí |
|---|---|---|---|
| SV1 | `codex/sv1-model-contract` | `tests/test_article_serialization.py`, `docs/team/sv1-model-contract.md` | Test hợp đồng DTO, giữ document đầu vào, ObjectId/datetime/ISO, slug và ID sai; không cần DB |
| SV2 | `codex/sv2-environment-check` | `data/check_env.py`, `tests/test_check_env.py`, `docs/team/sv2-environment-check.md` | Chế độ offline và ping dịch vụ có timeout; không ghi DB/lộ bí mật; lỗi có kiểm soát |
| SV3 | `codex/sv3-api-reference` | `data/gen_api_docs.py`, `tests/test_api_doc_generation.py`, `docs/API_REFERENCE.md`, `docs/team/sv3-api-reference.md` | Tài liệu API offline ổn định; không import app.py; đủ saved/health; kiểm tra cách lấy route |

Các file trên chưa được thực hiện trong bản nền; đây là phần thành viên tự làm. Tên người nhận thống nhất trong phân công của nhóm, không đưa MSSV/thông tin cá nhân vào source khi không cần.

Lưu ý đúng mã hiện tại: `to_dict()` trả `dd/mm/YYYY HH:mm`, không phải ISO. Import `app.py` tạo app và có thể tạo index; công cụ offline không dùng đường đó. Chỉ đọc các Blueprint chưa đủ `/api/health` vì route này nằm trong factory; phải đối chiếu/phân tích tĩnh phần đó. Tài liệu route không tự tương đương OpenAPI đầy đủ.

## Quy trình

1. Clone repo; kiểm tra `main` mới và cấu hình Git bằng danh tính/email gắn với tài khoản mình.
2. `git switch -c <nhanh-cua-ban> origin/main`; dùng đúng tên đã phân công.
3. Chỉ sửa trong phạm vi task. Không sửa lõi app, requirements, `__init__.py` hay `conftest.py` để ép test pass. Lỗi lõi mở issue riêng.
4. Kiểm tra file/secret, chạy test của mình và ghi lệnh/kết quả thật.
5. Stage từng file; commit nội dung có ý nghĩa rồi push nhánh; mở PR base `main`.
6. Một người khác review; trưởng nhóm thử kết quả hợp nhất trên worktree/clone riêng và DB test.
7. Merge lần lượt khi đạt; chạy lại kiểm tra trên main. Có thể dùng merge commit để giữ các commit và điểm tích hợp.

Mỗi PR cần: vấn đề, file thay đổi, cách kiểm tra, kết quả, giới hạn và link issue. Không tạo commit rỗng/đổi author/date để phân đều hoạt động. Không push thẳng main trong công việc thành viên.

## Kiểm tra trước hợp nhất

- Đối chiếu diff chỉ có file cho phép, không thêm `.env`, backup, `.venv`, log hoặc file báo cáo nhị phân.
- Công cụ mới không kết nối/ghi DB khi import; offline test dùng process mới để không bị module cache che tác động.
- Test theo [TESTING.md](TESTING.md); bản merge thử phải đúng SHA sẽ hợp nhất.
- So sánh core với mốc nền: app/config/models/services/controllers/views/static/requirements không đổi trong ba PR bổ sung.
- Khi có lỗi sau merge: dừng PR tiếp theo, tạo PR sửa hoặc revert đã review; không force push/reset lịch sử main.

Mỗi người giữ link commit, PR, nhận xét và log đã che bí mật, đồng thời giải thích được công việc. Hướng dẫn Word nội bộ và sản phẩm báo cáo nằm ngoài bản checkout source.
