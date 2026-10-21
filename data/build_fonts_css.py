"""
Sinh file CSS @font-face cuc bo cho font Be Vietnam Pro (tai ve tu Google Fonts).
Chay: python data/build_fonts_css.py
Ket qua: static/fonts/fonts.css
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSS_SRC = Path(r"D:\AndroidTemp\opencode\bevietnam.css")
OUT_DIR = Path(__file__).resolve().parent.parent / "static" / "fonts"


def main():
    if not CSS_SRC.exists():
        print(f"Khong tim thay {CSS_SRC}")
        return
    css = CSS_SRC.read_text(encoding="utf-8")
    urls = re.findall(r"url\((https://[^)]+\.woff2)\)", css)
    mapping = {}
    for index, url in enumerate(dict.fromkeys(urls), start=1):
        mapping[url] = f"bvp_{index}.woff2"

    for url, name in mapping.items():
        target = OUT_DIR / name
        if not target.exists():
            print(f"  [!] Thieu file font: {name}")

    for url, name in mapping.items():
        css = css.replace(url, name)

    # Bo ky tu khong phai ASCII (comment cua Google Fonts co thể bi loi encode)
    css = "".join(ch if ord(ch) < 128 else "?" for ch in css)

    header = (
        "/* Font Be Vietnam Pro - tai ve tu Google Fonts (dung offline khi demo).\n"
        "   File CSS duoc sinh boi data/build_fonts_css.py */\n\n"
    )
    (OUT_DIR / "fonts.css").write_text(header + css, encoding="utf-8")
    print(f"  + {OUT_DIR / 'fonts.css'}  ({len(mapping)} file font)")


if __name__ == "__main__":
    main()
