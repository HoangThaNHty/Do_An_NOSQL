# KẾ HOẠCH CHIA VIỆC NHÓM — ĐỀ TÀI 06

> **Mục đích:** mỗi thành viên có **commit thật** trên nhánh riêng, push từ **máy + tài khoản GitHub của mình**,
> rồi mở Pull Request để trưởng nhóm merge vào `main`.
>
> **Thời gian:** 45–60 phút/người · **Không cần cài MongoDB/Redis** · Không đụng vào code lõi.

---

## 0. Bối cảnh

- Project đã hoàn chỉnh trên `main` (14 commit): Flask + MongoDB + Redis, 20 test pass.
- 3 nhánh feature hiện **đang đứng ở commit khởi tạo**, chưa có commit riêng → cần mỗi bạn thêm việc thật.
- Mỗi bạn chỉ làm **1 việc nhỏ, độc lập**, không sửa file của người khác → **không bao giờ conflict**.

| Nhánh | Thành viên | Việc làm | File tạo mới |
|---|---|---|---|
| `feature/database-article-crud` | **SV1** | Viết unit test cho model bài viết | `tests/test_models.py` |
| `feature/redis-cache` | **SV2** | Script chẩn đoán môi trường (dùng chung cả nhóm) | `data/check_env.py` |
| `feature/session-performance` | **SV3** | Sinh tài liệu API tự động từ Flask | `data/gen_api_docs.py` + `docs/API_REFERENCE.md` |

> Cả 3 việc đều **có ích thật** cho báo cáo: tăng số test, có công cụ setup, có tài liệu API.

---

## 1. Nguyên tắc

1. **Mỗi người 1 nhánh**, tên nhánh đúng như bảng trên.
2. **Chỉ tạo file mới** trong phạm vi được giao — **không sửa** `app.py`, `services/*`, `controllers/*`, `views/*`.
3. **Không commit** `.env`, `.venv`, `__pycache__`.
4. **Không push thẳng `main`** — chỉ push nhánh của mình rồi mở PR.
5. Commit bằng **tài khoản GitHub của chính mình** (cấu hình `user.name` / `user.email`).

---

## 2. Chuẩn bị

### 2.1. Trưởng nhóm — đưa repo lên GitHub (làm 1 lần)

```powershell
cd D:\Do_AN_NOSQL

# 1) Xóa 3 nhánh cũ đang đứng ở commit khởi tạo (chưa có commit riêng)
git branch -D feature/database-article-crud feature/redis-cache feature/session-performance

# 2) Tạo repo TRỐNG trên github.com (đừng tick README/gitignore), rồi:
git remote add origin https://github.com/<username>/<ten-repo>.git
git branch -M main
git push -u origin main
```

Kiểm tra: mở GitHub thấy **14 commit**, nhánh mặc định `main`.

> Nếu chưa cài Git trên máy thành viên: https://git-scm.com/download/win (mặc định Next hết).

### 2.2. Thành viên — clone và cài đặt

```powershell
git clone https://github.com/<username>/<ten-repo>.git
cd <ten-repo>

# Môi trường Python (chỉ cần cho SV1 và SV3)
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

# File cấu hình (không bắt buộc cho 3 việc này, nhưng nên có)
copy .env.example .env
```

### 2.3. Cấu hình danh tính Git (bắt buộc — để commit đúng tên)

```powershell
git config user.name  "Nguyễn Văn A"
git config user.email "email-cua-ban@example.com"
```

> Dùng **email gắn với tài khoản GitHub** thì avatar sẽ hiện đúng người.
> Nếu không có, dùng email nào cũng được — commit vẫn ghi đúng tên.

### 2.4. Tạo nhánh làm việc

```powershell
git switch -c feature/<ten-nhanh-cua-ban>
```

---

## 3. TASK CARD — SV1

**Nhánh:** `feature/database-article-crud`
**Việc:** viết unit test cho `models/article.py`
**File tạo mới:** `tests/test_models.py`

### Yêu cầu

Viết **≥ 8 test** phủ 3 hàm: `slugify()`, `to_dict()`, `utcnow()`.

| Hàm | Trường hợp cần test | Kết quả mong đợi |
|---|---|---|
| `slugify` | `"AI tạo sinh"` | `ai-tao-sinh` |
| `slugify` | `"Lập trình Python 3.13"` | `lap-trinh-python-313` |
| `slugify` | `""` (chuỗi rỗng) | `bai-viet` |
| `slugify` | `"C++ & Java!!!"` | `c-java` |
| `to_dict` | document có `datetime` | field đó thành **chuỗi ISO** |
| `to_dict` | document có `ObjectId` | field đó thành **str** |
| `to_dict` | field bình thường (`title`) | giữ nguyên giá trị |
| `utcnow` | gọi hàm | có `tzinfo` (timezone-aware) |

### Gợi ý triển khai

```python
# tests/test_models.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.article import slugify, to_dict, utcnow

def test_slugify_...():
    assert slugify("AI tạo sinh") == "ai-tao-sinh"

# to_dict: tạo dict thủ công có datetime + ObjectId rồi kiểm tra
# utcnow: assert utcnow().tzinfo is not None
```

### Lệnh kiểm tra

```powershell
.venv\Scripts\python -m pytest tests/test_models.py -q
```

### Tiêu chí nghiệm thu

- [ ] ≥ 8 test, **tất cả PASS**
- [ ] Không cần MongoDB/Redis vẫn chạy được
- [ ] Không sửa file nào khác

### Commit

```powershell
git add tests/test_models.py
git commit -m "test(models): bo sung unit test cho slugify va to_dict"
git push -u origin feature/database-article-crud
```

---

## 4. TASK CARD — SV2

**Nhánh:** `feature/redis-cache`
**Việc:** script chẩn đoán môi trường — dùng chung cho cả nhóm trước buổi demo
**File tạo mới:** `data/check_env.py`

### Yêu cầu

Script in ra bảng kiểm tra và **không bị crash** khi service chưa chạy.

| Mục kiểm tra | Cách làm | Kết quả |
|---|---|---|
| Python | `sys.version_info` | `PASS` nếu ≥ 3.10 |
| Thư viện | `importlib.metadata.version("flask"/"pymongo"/"redis"/"pytest")` | `PASS` nếu đã cài |
| MongoDB | `socket.create_connection(("127.0.0.1", 27017), timeout=1)` | `PASS`/`FAIL` |
| Redis | `socket.create_connection(("127.0.0.1", 6379), timeout=1)` + `redis.Redis().ping()` | `PASS`/`FAIL` |
| Kết luận | nếu có FAIL thì in gợi ý sửa | `Start-Service MongoDB` / `data\start_redis.bat` |

### Định dạng đầu ra mong đợi

```
============================================================
  KIEM TRA MOI TRUONG - De tai 06
============================================================
  [PASS] Python            3.13.5
  [PASS] flask             3.1.x
  [PASS] pymongo           4.x
  [PASS] redis             6.x
  [FAIL] MongoDB           127.0.0.1:27017 - khong ket noi duoc
         -> Chay: Start-Service MongoDB
  [PASS] Redis             127.0.0.1:6379 - PONG
------------------------------------------------------------
  Ket qua: 5/6 PASS
============================================================
```

### Gợi ý triển khai

- Dùng `socket.create_connection` bọc `try/except OSError`.
- Dùng `sys.exit(0)` nếu tất cả PASS, `sys.exit(1)` nếu có FAIL.
- Thêm `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` để in tiếng Việt trên Windows.
- **Không** import `app.py` (tránh phụ thuộc Mongo/Redis).

### Tiêu chí nghiệm thu

- [ ] Chạy được cả khi **tắt** MongoDB và Redis (báo FAIL, không crash)
- [ ] Chạy được khi **bật** cả hai (báo PASS, exit code 0)
- [ ] Có gợi ý sửa cho từng mục FAIL

### Commit

```powershell
git add data/check_env.py
git commit -m "feat(devops): them script chan doan moi truong check_env.py"
git push -u origin feature/redis-cache
```

---

## 5. TASK CARD — SV3

**Nhánh:** `feature/session-performance`
**Việc:** sinh tài liệu API tự động từ Flask
**File tạo mới:** `data/gen_api_docs.py` + `docs/API_REFERENCE.md` (file này do script sinh ra)

### Yêu cầu

Script đọc `url_map` của Flask và ghi ra `docs/API_REFERENCE.md`.

| Yêu cầu | Chi tiết |
|---|---|
| Lấy route | `create_app().url_map.iter_rules()` |
| Bỏ route rác | bỏ `static`, bỏ method `HEAD` / `OPTIONS` |
| Cột bảng | `Method` · `Path` · `Endpoint` · `Mô tả` |
| Cột "Mô tả" | lấy từ `app.view_functions[endpoint].__doc__` (dòng đầu), nếu không có thì để trống |
| Sắp xếp | theo `Path` |
| Header file | tiêu đề + ngày sinh + số route |
| Chạy được | **không cần** MongoDB/Redis đang chạy |

### Gợi ý triển khai

```python
# data/gen_api_docs.py
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app

app = create_app()
rows = []
for rule in app.url_map.iter_rules():
    if rule.endpoint == "static":
        continue
    methods = sorted(m for m in rule.methods if m not in ("HEAD", "OPTIONS"))
    doc = (app.view_functions[rule.endpoint].__doc__ or "").strip().splitlines()
    rows.append((" / ".join(methods), str(rule.rule), rule.endpoint, doc[0] if doc else ""))

rows.sort(key=lambda r: r[1])
# ghi markdown vào docs/API_REFERENCE.md
```

### Tiêu chí nghiệm thu

- [ ] `docs/API_REFERENCE.md` có **≥ 25 route**, đúng định dạng bảng markdown
- [ ] Không có route `static`, không có `HEAD/OPTIONS`
- [ ] Chạy lại script cho ra cùng kết quả (trừ dòng ngày)

### Commit

```powershell
git add data/gen_api_docs.py docs/API_REFERENCE.md
git commit -m "docs(api): sinh tai lieu API tu url_map"
git push -u origin feature/session-performance
```

---

## 6. Mở Pull Request & merge (trưởng nhóm)

Sau khi cả 3 bạn push:

1. Vào GitHub → tab **Pull requests** → **New pull request**
2. `base: main` ← `compare: feature/...` → **Create pull request**
3. Trưởng nhóm bấm **Merge pull request** → chọn **Create a merge commit** (đừng chọn Squash)
4. Lặp lại cho 3 nhánh
5. Về máy, cập nhật:

```powershell
git switch main
git pull origin main
.venv\Scripts\python -m pytest tests/ -q
```

Kỳ vọng: **20 + ≥ 8 test của SV1 = ≥ 28 test PASS**.

> Chọn **merge commit** (không squash) để GitHub giữ nguyên tác giả từng commit và vẽ graph phân nhánh.

---

## 7. Checklist trước buổi thuyết trình

- [ ] GitHub có **3 nhánh** + **3 PR đã merge** + **3 tác giả** trong tab Insights → Contributors
- [ ] `main` có ≥ 28 test PASS
- [ ] `docs/API_REFERENCE.md` tồn tại
- [ ] `data/check_env.py` chạy trên máy từng thành viên
- [ ] Mỗi thành viên clone về máy mình, chạy `python data/check_env.py` + mở web được (nếu có MongoDB/Redis)
- [ ] Không có file `.env` trên GitHub

---

## 8. Phương án dự phòng

| Tình huống | Cách xử lý |
|---|---|
| Thành viên không cài được Python | Đổi sang việc **chỉ docs**: viết `docs/CACHE_DESIGN.md` (SV2) hoặc `docs/SESSION_DESIGN.md` (SV3) — vẫn là commit thật, có nội dung |
| Không có Git trên máy | Cài Git for Windows, hoặc dùng **GitHub Desktop** (clone → commit → push bằng GUI) |
| Push bị từ chối `non-fast-forward` | `git pull --rebase origin <nhánh>` rồi push lại |
| Commit hiện sai tên | `git commit --amend --author="Tên <email>" --no-edit` rồi `git push --force-with-lease` |
| Thành viên chưa có tài khoản GitHub | Tạo tài khoản (2 phút), hoặc dùng email bất kỳ — commit vẫn đúng tên, chỉ thiếu avatar |

---

## 9. Prompt để trao đổi với AI khác

Dán nguyên khối này cho AI mà thành viên đang dùng:

```
Bối cảnh: tôi là thành viên nhóm làm đồ án Flask + MongoDB + Redis (Đề tài 06).
Repo: https://github.com/<username>/<ten-repo>
Nhánh của tôi: feature/<ten-nhanh>
Nhiệm vụ của tôi: <dán nguyên Task Card ở mục 3/4/5>

Ràng buộc:
- Chỉ tạo file mới trong phạm vi được giao, KHÔNG sửa file khác.
- Không commit .env, .venv, __pycache__.
- Code phải chạy được trên Windows, Python 3.13.

Hãy giúp tôi:
1. Viết code hoàn chỉnh cho file được giao.
2. Cho tôi lệnh chạy để kiểm tra.
3. Soát lại xem có vi phạm ràng buộc nào không.
```

---

## 10. Nếu giảng viên hỏi về phân công

| Câu hỏi | Trả lời |
|---|---|
| Ai làm phần nào? | SV1: model + CRUD + test model · SV2: cache + công cụ môi trường · SV3: session + tài liệu API + đo hiệu năng |
| Sao `main` nhiều commit một tác giả? | Đó là các commit **tích hợp** của trưởng nhóm; phần của từng bạn nằm trên nhánh riêng và đã merge qua PR |
| Kiểm chứng ở đâu? | GitHub → **Insights → Contributors**; **Pull requests → Closed** (3 PR); **Network** (graph phân nhánh) |
| Mỗi bạn chạy thử chưa? | Mỗi bạn clone về máy, chạy `python data/check_env.py` và `pytest` — có ảnh chụp màn hình |
