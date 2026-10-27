# Bàn giao công việc và nhánh GitHub

Cập nhật 28/10/2026. `main` là bản tích hợp để demo, hiện có hai role `admin` và `reader`. Hai đầu việc của thành viên dưới đây bổ sung cho source đang chạy, không yêu cầu viết lại CRUD/cache/session. PR ghi nhận phần thực tế làm thêm; tên nhánh không xác định tác giả mã cũ.

## 1. Phân công

| Mã | Nhánh đã chuẩn bị từ main | Công việc mới |
|---|---|---|
| SV1 | `main` | Quản lý bản tích hợp, review PR và kiểm thử sau merge; không cần thêm nhánh cá nhân |
| SV2 | `feature/environment-check` | Công cụ kiểm tra môi trường và kết nối MongoDB/Redis chỉ đọc |
| SV3 | `docs/api-reference` | Sinh tài liệu API offline và kiểm tra độ đúng |

Tên người nhận và MSSV nằm trong Word bàn giao nội bộ. Các nhánh `feature/*` cũ giữ nguyên để đối chiếu, không dùng thay hai nhánh công việc mới. Không xóa/ghi đè commit đã có của thành viên.

### SV1 Quản lý main và tích hợp

Không cần tạo nhánh riêng chỉ để có thêm commit. Thực hiện review, kiểm thử bản merge thử, hợp nhất từng PR và kiểm tra lại main theo mục 3. Nếu phát sinh sửa code riêng, tạo nhánh ngắn theo công việc cụ thể rồi mở PR.

### SV2 Công cụ kiểm tra môi trường

**Chỉ thêm:** `data/check_env.py`, `tests/test_check_env.py`, `docs/team/environment-check.md`.

- `--offline`: kiểm tra Python và dependency đã cài, không kết nối mạng/DB. Thiếu package phải có thông báo rõ.
- `--services`: đọc cấu hình hiện có, ping MongoDB và Redis đúng giao thức; có timeout kết nối/đọc, đóng client sau kiểm tra.
- Xuất PASS/WARN/FAIL, mã thoát 0 khi đạt và 1 khi có lỗi kiểm tra; không in mật khẩu, URI chứa credentials hoặc nội dung `.env`.
- Không import `app.py`, không tạo index/seed, không ghi/xóa dữ liệu hay khởi động/dừng dịch vụ. Import module công cụ không tự chạy kiểm tra.
- Test bằng mock: thành công, thiếu package, timeout, lỗi xác thực và mất kết nối; xác minh offline không tạo client/kết nối.
- Nghiệm thu: chạy `data/check_env.py --offline` và `python -m pytest tests/test_check_env.py -q` qua Python trong `.venv`. Chỉ chạy thêm `--services` khi đã có DB.

### SV3 Tài liệu API offline

**Chỉ thêm:** `data/gen_api_docs.py`, `tests/test_api_doc_generation.py`, `docs/API_REFERENCE.md`, `docs/team/api-reference.md`.

- Lấy route từ source hiện tại bằng phân tích tĩnh, hoặc đăng ký Blueprint trên Flask tạm; không import `app.py`, gọi `create_app()` hay gọi handler.
- Nếu dùng Blueprint, phải bổ sung `/api/health` bằng phân tích tĩnh `app.py`. Đủ API bài viết, auth, admin, cache và saved; chỉ lấy đường dẫn `/api/`.
- Bảng gồm Method, Path, Endpoint, Mô tả, Nguồn; bỏ HEAD/OPTIONS, loại trùng, sắp xếp ổn định, escape ký tự Markdown. Quyền truy cập cần đối chiếu decorator, không đoán theo tên hàm.
- Chạy hai lần phải ra cùng nội dung, không chèn timestamp biến đổi. Tài liệu route chưa phải OpenAPI đầy đủ.
- Test route đại diện gồm saved/health, method, trùng lặp, escape và tính ổn định; dùng process mới để kiểm tra không import app/kết nối DB.
- Nghiệm thu: chạy `data/gen_api_docs.py`, chạy lại không đổi file; `python -m pytest tests/test_api_doc_generation.py -q` đạt qua Python trong `.venv` khi không bật DB.

## 2. Thành viên thao tác

Chủ repo mời hai thành viên vào Collaborators; mỗi người dùng tài khoản và email liên kết GitHub của mình. Thực hiện từng lệnh, xử lý lỗi trước khi chạy tiếp.

```powershell
git clone https://github.com/HoangThaNHty/Do_An_NOSQL.git
cd Do_An_NOSQL
git config user.name "Ho ten cua ban"
git config user.email "Email lien ket GitHub cua ban"
git fetch origin
# Ví dụ SV2; SV3 dùng origin/docs/api-reference
git switch --track origin/feature/environment-check
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Nếu đã clone, bỏ hai lệnh đầu. Nếu nhánh đã có ở máy, dùng `git switch <nhánh>` rồi `git pull --ff-only`; không tạo/xóa lại nhánh. Các task offline không cần tạo `.env`.

Sau khi làm và chạy kiểm tra:

```powershell
git status --short
git diff --check
git diff --name-only origin/main...HEAD
# Stage từng file đúng danh sách được giao, không dùng git add .
git add <duong-dan-file>
git diff --cached --name-only
git commit -m "Mo ta cong viec thuc te da hoan thanh"
git push -u origin HEAD
```

Trước commit, đọc cả file mới và diff đang stage. Mở PR trên GitHub: **base `main`, compare nhánh của mình**. PR và file `docs/team/...md` ghi ngắn: việc đã làm, lệnh kiểm tra, kết quả thật, giới hạn. Không dùng commit rỗng, đổi tác giả hoặc sao chép nguyên code đã có để ghi nhận đóng góp.

## 3. Người quản lý main nghiệm thu

1. Review diff chỉ có file được giao; không có `.env`, log, backup hoặc dữ liệu cá nhân. Không sửa `app.py`, `config.py`, `models/`, `services/`, `controllers/`, `views/`, `static/`, `requirements.txt`, `tests/conftest.py`, `__init__.py` trong hai task này. Lỗi lõi báo riêng.
2. Chạy test của task trên bản merge thử trong clone riêng. SV2 kiểm tra thêm ping thật; SV3 đối chiếu route với runtime trên DB test. Các công cụ offline phải chạy được khi không bật DB.
3. Chạy bộ test theo [TESTING.md](TESTING.md) trên MongoDB `nosql_news_test` và Redis DB riêng; **bộ test có dọn dữ liệu test**, không trỏ vào DB demo. Thử các luồng chính trên DB demo riêng: đọc/tìm, đăng nhập, CRUD, cache và lưu bài.
4. Merge từng PR bằng **Create a merge commit** sau khi đạt; kiểm tra lại bản tích hợp trước PR tiếp theo. Nếu có conflict, xử lý và kiểm thử lại; không force push main.

Mốc nền ban đầu: `baseline-diem-tin-v1`; bản source đối chiếu cho đợt bàn giao này là `daa2306`. Hai nhánh công việc mới được tạo cùng từ commit main chứa hướng dẫn cập nhật này. Việc hoàn thành được xác nhận bằng thay đổi file, kết quả chạy và PR được review, không chỉ bằng số commit.
