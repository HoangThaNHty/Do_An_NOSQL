
"""
Sinh tai lieu API offline cho do an Diem Tin.

- Phan tich AST, khong import app.py hay controllers.
- Khong khoi tao Flask, MongoDB hoac Redis.
- Chi xuat cac route bat dau bang /api/.
- Ket qua on dinh giua cac lan chay.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "API_REFERENCE.md"

METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
SHORTCUTS = {
    "get": "GET",
    "post": "POST",
    "put": "PUT",
    "patch": "PATCH",
    "delete": "DELETE",
}

DESCRIPTIONS = {
    "/api/health": "Kiem tra trang thai he thong",
    "/api/articles": "Danh sach hoac quan ly bai viet",
    "/api/articles/search": "Tim kiem bai viet",
    "/api/articles/suggestions": "Goi y tim kiem",
    "/api/auth/register": "Dang ky tai khoan",
    "/api/auth/login": "Dang nhap",
    "/api/auth/session": "Kiem tra phien dang nhap",
    "/api/auth/logout": "Dang xuat",
    "/api/cache/stats": "Thong ke cache",
    "/api/cache/sessions": "Thong tin session cache",
    "/api/cache/keys": "Danh sach khoa cache",
    "/api/cache/reset": "Dat lai cache",
    "/api/saved": "Danh sach bai viet da luu",
}


def literal(node, default=None):
    """Doc gia tri hang so tu AST."""
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, RecursionError):
        return default


def markdown_escape(value):
    """Escape ky tu co the lam hong bang Markdown."""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def join_path(prefix, path):
    """Ghep Blueprint prefix va route."""
    prefix = prefix.rstrip("/")
    return prefix + "/" + path.lstrip("/")


def get_blueprints(tree):
    """Tim ten bien Blueprint va url_prefix."""
    blueprints = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue

        call = node.value

        if not isinstance(call, ast.Call):
            continue

        if not isinstance(call.func, ast.Name):
            continue

        if call.func.id != "Blueprint":
            continue

        prefix = ""

        for keyword in call.keywords:
            if keyword.arg == "url_prefix":
                value = literal(keyword.value)
                if isinstance(value, str):
                    prefix = value

        for target in node.targets:
            if isinstance(target, ast.Name):
                blueprints[target.id] = prefix

    return blueprints


def get_methods(decorator, decorator_name):
    """Lay HTTP methods tu decorator Flask."""
    if decorator_name in SHORTCUTS:
        return [SHORTCUTS[decorator_name]]

    for keyword in decorator.keywords:
        if keyword.arg == "methods":
            values = literal(keyword.value)

            if isinstance(values, (list, tuple, set)):
                return sorted({
                    str(value).upper()
                    for value in values
                    if str(value).upper() in METHODS
                })

    return ["GET"]


def decorator_label(node):
    """Lay ten decorator de doi chieu quyen truy cap."""
    if isinstance(node, ast.Call):
        return decorator_label(node.func)

    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        return node.attr

    return ""


def describe_route(path, function_node):
    """Lay mo ta tu docstring hoac bang mo ta."""
    docstring = ast.get_docstring(function_node)

    if docstring:
        return " ".join(docstring.strip().split())

    if path in DESCRIPTIONS:
        return DESCRIPTIONS[path]

    if path.startswith("/api/saved"):
        return "Quan ly bai viet da luu"

    if path.startswith("/api/cache/invalidate"):
        return "Xoa cache cua bai viet"

    return "Chua co mo ta trong source"


def scan_file(file_path):
    """Phan tich route trong mot file Python."""
    source = file_path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(file_path))

    blueprints = get_blueprints(tree)
    results = []

    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue

        permissions = []

        for decorator in node.decorator_list:
            name = decorator_label(decorator)

            if name in {
                "login_required",
                "admin_required",
                "admin_api_required",
            }:
                permissions.append(name)

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            func = decorator.func

            if not isinstance(func, ast.Attribute):
                continue

            if not isinstance(func.value, ast.Name):
                continue

            decorator_name = func.attr

            if decorator_name not in {
                "route", *SHORTCUTS.keys()
            }:
                continue

            if not decorator.args:
                continue

            path = literal(decorator.args[0])

            if not isinstance(path, str):
                continue

            owner = func.value.id
            prefix = blueprints.get(owner, "")

            # app.py dung @app.get("/api/health")
            if owner != "app" and owner not in blueprints:
                continue

            full_path = join_path(prefix, path)

            if not full_path.startswith("/api/"):
                continue

            methods = get_methods(
                decorator, decorator_name
            )

            description = describe_route(
                full_path, node
            )

            if permissions:
                description += (
                    " [Decorator: "
                    + ", ".join(sorted(set(permissions)))
                    + "]"
                )

            endpoint = node.name
            if owner in blueprints:
                endpoint = owner + "." + node.name

            relative_file = file_path.relative_to(ROOT)
            source_location = (
                f"{relative_file.as_posix()}:{node.lineno}"
            )

            for method in methods:
                results.append({
                    "method": method,
                    "path": full_path,
                    "endpoint": endpoint,
                    "description": description,
                    "source": source_location,
                })

    return results


def collect_routes(root=ROOT):
    """Thu thap va loai trung API."""
    files = [root / "app.py"]
    files.extend(sorted(
        (root / "controllers").glob("*.py")
    ))

    unique = {}

    for file_path in files:
        if not file_path.is_file():
            continue

        for route in scan_file(file_path):
            key = (
                route["method"],
                route["path"],
                route["endpoint"],
            )
            unique[key] = route

    return sorted(
        unique.values(),
        key=lambda item: (
            item["path"],
            item["method"],
            item["endpoint"],
            item["source"],
        ),
    )


def generate_markdown(routes):
    """Tao noi dung Markdown on dinh."""
    lines = [
        "# API REFERENCE - DIEM TIN",
        "",
        "Tai lieu duoc sinh tu source Python bang AST.",
        "",
        "**Pham vi:** Chi cac route bat dau bang `/api/`.",
        "",
        "**Luu y:** Day la danh sach route, "
        "khong phai dac ta OpenAPI day du.",
        "",
        f"**Tong so method-route:** {len(routes)}",
        "",
        "| Method | Path | Endpoint | Mo ta | Nguon |",
        "|---|---|---|---|---|",
    ]

    for route in routes:
        values = [
            route["method"],
            route["path"],
            route["endpoint"],
            route["description"],
            route["source"],
        ]

        lines.append(
            "| "
            + " | ".join(
                markdown_escape(value)
                for value in values
            )
            + " |"
        )

    lines.extend([
        "",
        "## Gioi han",
        "",
        "- Khong thuc thi handler.",
        "- Khong ket noi MongoDB hoac Redis.",
        "- Quyen truy cap chi duoc ghi khi "
        "phat hien decorator trong source.",
        "- Khong suy doan request/response schema.",
        "- Route khai bao dong co the khong "
        "duoc phat hien bang phan tich tinh.",
        "",
    ])

    return "\n".join(lines)


def main():
    routes = collect_routes()
    content = generate_markdown(routes)

    OUTPUT.parent.mkdir(
        parents=True, exist_ok=True
    )
    OUTPUT.write_text(
        content, encoding="utf-8"
    )

    print("SINH TAI LIEU API THANH CONG")
    print(f"So method-route: {len(routes)}")
    print(f"File: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
