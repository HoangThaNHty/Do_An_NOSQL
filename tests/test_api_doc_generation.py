
import ast
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "data" / "gen_api_docs.py"
OUTPUT = ROOT / "docs" / "API_REFERENCE.md"


def run_generator():
    return subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def read_rows():
    lines = OUTPUT.read_text(encoding="utf-8").splitlines()
    return [
        line.split(" | ")
        for line in lines
        if line.startswith("| ")
        and not line.startswith("| Method")
    ]


def test_generator_runs():
    result = run_generator()
    assert result.returncode == 0, result.stderr
    assert OUTPUT.exists()


def test_representative_routes():
    result = run_generator()
    assert result.returncode == 0

    content = OUTPUT.read_text(encoding="utf-8")

    assert "| GET | /api/health |" in content
    assert "| GET | /api/saved |" in content
    assert "| PUT | /api/saved/<article_id> |" in content
    assert "| DELETE | /api/saved/<article_id> |" in content
    assert "| POST | /api/auth/login |" in content
    assert "| GET | /api/cache/stats |" in content


def test_methods_and_no_duplicates():
    result = run_generator()
    assert result.returncode == 0

    rows = read_rows()
    keys = []

    for row in rows:
        method = row[0].removeprefix("| ").strip()
        path = row[1].strip()
        endpoint = row[2].strip()

        assert method in {
            "GET", "POST", "PUT", "PATCH", "DELETE"
        }
        assert path.startswith("/api/")
        keys.append((method, path, endpoint))

    assert len(keys) == len(set(keys))


def test_stable_output():
    first = run_generator()
    assert first.returncode == 0

    hash1 = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()

    second = run_generator()
    assert second.returncode == 0

    hash2 = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()

    assert hash1 == hash2


def test_markdown_escaping():
    source = GENERATOR.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert tree is not None

    # Test ham escape trong process rieng,
    # khong import app.py.
    code = (
        "import runpy; "
        "d=runpy.run_path('data/gen_api_docs.py'); "
        "print(d['markdown_escape']('A|B'))"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == r"A\|B"


def test_no_app_import_or_db_connection():
    # Chay trong process moi va chan import
    # app, pymongo, redis de phat hien side effects.
    code = """
import builtins
import runpy

original_import = builtins.__import__

def guarded_import(name, *args, **kwargs):
    root = name.split('.')[0]
    if root in {'app', 'pymongo', 'redis'}:
        raise RuntimeError('Forbidden import: ' + name)
    return original_import(name, *args, **kwargs)

builtins.__import__ = guarded_import
runpy.run_path('data/gen_api_docs.py', run_name='__main__')
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
