"""
data/fetch_images.py - TAI ANH THAT TU MANG cho du lieu mau

Nguon: Openverse API (https://api.openverse.org) - anh that, tu kho CC
(CC0/PDM/CC-BY), co thong tin tac gia + giay phep de ghi vao bao cao.

Moi chuyen muc lay 'N' anh tuong ung theo tu khoa, sau do:
    - cat ve kich thuoc chuan 1200x675 (16:9) cho trang tin tuc
    - nen JPEG chat luong 80 -> dung chung cho ca du an
    - ghi lai file uy quyen (credits) phuc vu bao cao

Chay:
    python data/fetch_images.py            # tai 5 anh cho moi chuyen muc
    python data/fetch_images.py --count 8  # tai 8 anh/chuyen muc
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Windows console mac dinh la cp1252 -> can chuyen sang utf-8 de in duoc tieng Viet
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import config  # noqa: E402

API_URL = "https://api.openverse.org/v1/images/"
USER_AGENT = "nosql-news-demo/1.0 (student project)"
TARGET_SIZE = (1200, 675)
MIN_WIDTH = 700

# Tu khoa tieng Anh - Openverse tim anh tot hon voi tieng Anh
QUERIES = {
    "Cong nghe": [
        "data center server room",
        "computer code screen programming",
        "smartphone technology news",
        "circuit board electronics",
        "robot artificial intelligence",
        "wireless network router",
    ],
    "Kinh te": [
        "stock exchange trading floor",
        "bank of vietnam building",
        "container ship port crane",
        "supermarket shelves shopping",
        "office towers skyline business",
        "textile factory workers production",
    ],
    "The thao": [
        "football stadium crowd",
        "swimming pool competition",
        "basketball arena court",
        "marathon road race runners",
        "tennis court player",
        "volleyball match indoor",
    ],
    "Khoa hoc": [
        "telescope observatory stars",
        "research laboratory scientist",
        "rocket launch space",
        "solar power plant panels",
        "hospital medical equipment",
        "earth from space satellite",
    ],
    "Xa hoi": [
        "hanoi street people",
        "ho chi minh city street",
        "public library people reading",
        "community volunteers group",
        "vietnam market street",
        "students classroom school",
    ],
    "Doi song": [
        "vegetables healthy food table",
        "coffee shop interior table",
        "people running park morning",
        "cooking food kitchen",
        "family home living room",
        "yoga wellness exercise",
    ],
}

# Chi lay anh dung thuong thuoc (cho phep su dung thuong mai)
LICENSE_FILTER = "cc0,pdm"

# Tu khoa cam - loai bo anh khong phu hop voi du an sinh vien
BLOCK_KEYWORDS = [
    "cannabis", "weed", "marijuana", "drug", "nude", "naked", "porn", "sex",
    "alcohol", "beer", "wine", "cigarette", "smoking", "gun", "weapon", "war",
    "corpse", "blood", "injury", "accident", "dead body", "protest violence",
    "showbooth", "halloween", "graffiti", "prison", "military tank", "corpse",
    "disabled", "cancer patient", "covid patient", "bicycle", "motorbike",
    "trump", "president", "graduation", "fish-eye", "julia", "vim", "blur",
    "statue", "cemetery", "military", "soldier", "police", "prisoner",
]

# Nguon uu tien: anh chup chat luong cao, dung thuong thuoc
PREFERRED_SOURCES = ("wikimedia", "stocksnap", "rawpixel", "nappy", "flickr")


def _get_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=40) as response:
        return json.loads(response.read().decode("utf-8"))


def search_images(query, page_size=15):
    """Tra ve danh sach anh ung vien theo tu khoa (loc them tu khoa cam)."""
    params = urllib.parse.urlencode(
        {
            "q": query,
            "page_size": page_size,
            "license": LICENSE_FILTER,
            "aspect_ratio": "wide",
            "extension": "jpg",
            "mature": "false",
        }
    )
    try:
        data = _get_json(f"{API_URL}?{params}")
    except Exception as exc:  # noqa: BLE001
        print(f"    [!] Loi khi tim '{query}': {exc}")
        return []

    results = []
    seen_titles = set()
    for item in data.get("results", []):
        title = (item.get("title") or "").lower()
        raw_tags = item.get("tags") or []
        tags = " ".join(
            (t.get("name") if isinstance(t, dict) else str(t)) for t in raw_tags
        ).lower()
        blob = f"{title} {tags}"
        if any(bad in blob for bad in BLOCK_KEYWORDS):
            continue
        if item.get("width") and item["width"] < MIN_WIDTH:
            continue
        # Bo trung tieu de (nhieu anh cung mot su kien)
        key = title[:40]
        if key in seen_titles:
            continue
        seen_titles.add(key)
        results.append(item)

    # Uu tien nguon co chat luong anh tot
    results.sort(key=lambda it: 0 if (it.get("source") or "") in PREFERRED_SOURCES else 1)
    return results


def download_and_process(url, out_path):
    """Tai anh, cat 16:9 va nen JPEG. Tra ve (ok, width, height)."""
    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        if len(raw) > 12_000_000:  # anh qua lon -> bo qua
            return False, 0, 0
        import io

        image = Image.open(io.BytesIO(raw)).convert("RGB")
        width, height = image.size
        if width < MIN_WIDTH:
            return False, width, height

        # Cat theo kich thuoc chuan 16:9 (can giua)
        target_ratio = TARGET_SIZE[0] / TARGET_SIZE[1]
        current_ratio = width / height
        if current_ratio > target_ratio:
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            image = image.crop((left, 0, left + new_width, height))
        else:
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            image = image.crop((0, top, width, top + new_height))
        image = image.resize(TARGET_SIZE, Image.LANCZOS)
        image.save(out_path, "JPEG", quality=80, optimize=True, progressive=True)
        return True, TARGET_SIZE[0], TARGET_SIZE[1]
    except Exception as exc:  # noqa: BLE001
        print(f"    [!] Khong tai duoc anh: {exc}")
        return False, 0, 0


def main():
    parser = argparse.ArgumentParser(description="Tai anh that cho du lieu mau")
    parser.add_argument("--count", type=int, default=5, help="So anh cho moi chuyen muc")
    parser.add_argument("--out", default=None, help="Thu muc luu anh (mac dinh static/images)")
    args = parser.parse_args()

    out_dir = Path(args.out) if args.out else (config.STATIC_FOLDER / "images")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 68)
    print("  TAI ANH THAT TU OPENVERSE (anh CC, dung cho thuong mai)")
    print("=" * 68)
    print(f"  Thu muc luu: {out_dir}")

    credits = []
    index = 0
    for category, queries in QUERIES.items():
        print(f"\n[{category}]")
        got = 0
        seen_urls = set()
        for query in queries:
            if got >= args.count:
                break
            for item in search_images(query):
                if got >= args.count:
                    break
                url = item.get("url")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                index += 1
                filename = f"news_{index:03d}.jpg"
                ok, w, h = download_and_process(url, out_dir / filename)
                if not ok:
                    continue
                got += 1
                credits.append(
                    {
                        "file": f"/static/images/{filename}",
                        "category": category,
                        "title": item.get("title"),
                        "creator": item.get("creator"),
                        "license": f"{item.get('license')} {item.get('license_version') or ''}".strip(),
                        "source": item.get("foreign_landing_url"),
                        "width": w,
                        "height": h,
                    }
                )
                print(f"  + {filename}  <- {query}  ({item.get('title', '')[:52]})")
                time.sleep(0.4)  # rat nhe de khong gay tai
        print(f"  -> Tong: {got} anh")

    # Luu thong tin uy quyen
    credits_file = out_dir / "credits.json"
    credits_file.write_text(json.dumps(credits, indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Danh sach anh dung trong du lieu mau", "",
          "Anh lay tu [Openverse](https://openverse.org) - cac anh deu dung giay phep",
          "cho phep su dung thuong mai. Khi trich dan, ghi nguon nhu sau.", "",
          "| File | Chuyen muc | Tac gia | Giay phep | Nguon |", "|---|---|---|---|---|"]
    for c in credits:
        md.append(
            f"| `{c['file']}` | {c['category']} | {c.get('creator') or '-'} | "
            f"{c.get('license') or '-'} | [{c.get('title') or '-'}]({c.get('source') or ''}) |"
        )
    (out_dir / "CREDITS.md").write_text("\n".join(md), encoding="utf-8")

    total_kb = sum(f.stat().st_size for f in out_dir.glob("*.jpg")) / 1024
    print("\n" + "=" * 68)
    print(f"  Tong: {len(credits)} anh  |  dung luong: {total_kb:.0f} KB")
    print(f"  File uy quyen: {credits_file}")
    print(f"  Bang uy quyen : {out_dir / 'CREDITS.md'}")
    print("=" * 68)


if __name__ == "__main__":
    main()
