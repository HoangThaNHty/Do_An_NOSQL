"""Kiểm tra hai quyền admin/reader; tự dọn bài được tạo để kiểm thử."""
import sys
import requests
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = "http://127.0.0.1:5000"
CHECKS = [
    ("Trang chủ", "GET", "/", (200, 200)),
    ("Danh sách bài", "GET", "/articles", (200, 200)),
    ("Trang cá nhân", "GET", "/profile", (200, 200)),
    ("Quản trị", "GET", "/admin/", (200, 302)),
    ("Quản lý bài viết", "GET", "/admin/articles", (200, 302)),
    ("Tạo bài (form)", "GET", "/admin/articles/create", (200, 302)),
    ("Người dùng", "GET", "/admin/users", (200, 302)),
    ("Bảng cache", "GET", "/admin/cache", (200, 302)),
    ("Phiên người dùng", "GET", "/api/cache/sessions", (200, 403)),
    ("Tạo bài (API)", "POST", "/api/articles", (201, 403)),
]

def main():
    results = {}
    for role in ("admin", "reader"):
        with requests.Session() as session:
            login = session.post(BASE + "/api/auth/login", json={"identifier": role, "password": "123456"}, timeout=10)
            if login.status_code != 200:
                print(f"Không đăng nhập được tài khoản {role}")
                return 1
            try:
                for label, method, path, expected in CHECKS:
                    response = session.request(method, BASE + path, timeout=10, allow_redirects=False,
                        **({"json": {"title": "Bài kiểm tra quyền tạm thời", "content": "Nội dung kiểm thử.", "category": "Công nghệ"}} if method == "POST" else {}))
                    results[(label, role)] = response.status_code
                    if method == "POST" and response.status_code == 201:
                        aid = response.json()["data"]["_id"]
                        session.delete(BASE + "/api/articles/" + aid, timeout=10).raise_for_status()
            finally:
                session.post(BASE + "/api/auth/logout", timeout=10)
    passed = 0
    for label, _, _, expected in CHECKS:
        actual = tuple(results[(label, role)] for role in ("admin", "reader"))
        ok = actual == expected
        passed += ok
        print(f"{label}: admin={actual[0]}, reader={actual[1]} — {'PASS' if ok else 'FAIL'}")
    print(f"{passed}/{len(CHECKS)} kiểm tra đúng quyền")
    return 0 if passed == len(CHECKS) else 1

if __name__ == "__main__":
    raise SystemExit(main())
