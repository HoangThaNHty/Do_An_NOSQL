"""
data/check_roles.py - KIEM TRA PHAN QUYEN THEO 3 ROLE TAI KHOAN

Dung de chung minh phan quyen trong buoi demo:
    admin  : toan quyen (quan ly bai viet, nguoi dung, xem bang cache)
    editor : quan ly noi dung (them/sua/xoa bai viet), KHONG xem danh sach nguoi dung
    reader : chi doc tin tuc, KHONG vao duoc trang quan tri

Chay:  python data/check_roles.py
"""

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:5000"
PASSWORD = "123456"

ACCOUNTS = [
    ("admin", "Quan tri vien"),
    ("editor", "Bien tap vien"),
    ("reader", "Nguoi doc"),
]

# (nhan, duong dan, ky vong theo role) - ky vong: 200 = duoc, 302 = bi chuyen huong, 401 = tu choi
CHECKS = [
    ("Doc trang chu", "/", (200, 200, 200)),
    ("Doc danh sach bai viet", "/articles", (200, 200, 200)),
    ("Doc trang tai khoan", "/profile", (200, 200, 200)),
    ("Vao trang quan tri", "/admin/", (200, 200, 302)),
    ("Quan ly bai viet", "/admin/articles", (200, 200, 302)),
    ("Them bai viet moi", "/admin/articles/create", (200, 200, 302)),
    ("Danh sach nguoi dung", "/admin/users", (200, 302, 302)),
    ("Bang dieu khien cache", "/admin/cache", (200, 200, 302)),
    ("Tao bai viet qua API", "/api/articles", (201, 201, 403)),
]


def login(session, username):
    response = session.post(
        f"{BASE}/api/auth/login",
        json={"identifier": username, "password": PASSWORD},
        timeout=15,
    )
    return response.status_code == 200, response.json()


def main():
    print("=" * 96)
    print("  BANG PHAN QUYEN THEO ROLE - De tai 06")
    print("=" * 96)

    results = {}
    for username, label in ACCOUNTS:
        session = requests.Session()
        ok, data = login(session, username)
        if not ok:
            print(f"[!] Dang nhap that bai: {username} - {data.get('error')}")
            print("    Hay chay: python data/seed_articles.py --reset")
            return
        role = data["data"]["user"]["role"]
        results[role] = {}
        for name, path, _ in CHECKS:
            if name == "Tao bai viet qua API":
                response = session.post(
                    f"{BASE}{path}",
                    json={"title": "Kiem tra phan quyen", "content": "Kiem tra role"},
                    timeout=15,
                )
            else:
                response = session.get(f"{BASE}{path}", timeout=15, allow_redirects=False)
            results[role][name] = response.status_code
        session.post(f"{BASE}/api/auth/logout", timeout=15)

    print(f"{'Chuc nang':<26}{'admin':>10}{'editor':>10}{'reader':>10}   Ky vong")
    print("-" * 96)
    ok_all = True
    for name, _, expected in CHECKS:
        row = []
        for role in ("admin", "editor", "reader"):
            code = results.get(role, {}).get(name, "-")
            row.append(code)
        exp = "/".join(str(x) for x in expected)
        good = all(results.get(r, {}).get(name) == e for r, e in zip(("admin", "editor", "reader"), expected))
        ok_all = ok_all and good
        print(f"{name:<26}{row[0]:>10}{row[1]:>10}{row[2]:>10}   {exp}  {'OK' if good else 'SAI'}")
    print("-" * 96)
    print("Ket qua:", "TAT CA DUNG - phan quyen hoat dong nhu mong doi" if ok_all else "CO SAI - can kiem tra lai")
    print("=" * 96)
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
