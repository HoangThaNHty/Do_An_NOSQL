"""
scripts/plot_benchmark.py - VE BIE DO SO SANH THOI GIAN MONGODB vs REDIS (Chuong 8)

Doc ket qua tu scripts/result_benchmark.json va ve:
    - Bieu do cot so sanh thoi gian phan hoi (ms) giua MongoDB va Redis
    - Bieu do duong: phan bo thoi gian theo cac lan do

Chay:  python scripts/plot_benchmark.py
Ket qua: docs/figures/bieu_do_hieu_nang.png
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # khong mo cua so khi ve (phuc vu may chay khong co man hinh)
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RESULT_FILE = Path(__file__).resolve().parent / "result_benchmark.json"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "figures"

LABELS = {
    "article_detail": "Chi tiet bai viet",
    "article_list": "Danh sach bai viet",
    "search": "Tim kiem",
    "article_detail_network": "Chi tiet bai viet (mo phong RTT 50ms)",
    "http_request": "HTTP request (tab Network F12)",
}


def main():
    if not RESULT_FILE.exists():
        print("Chua co ket qua benchmark. Chay:  python scripts/benchmark.py")
        return
    data = json.loads(RESULT_FILE.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------- Bieu do 1: so sanh trung binh ----------------
    scenarios = [k for k in LABELS if k in data]
    mongo_avg = [data[k]["mongodb"]["avg"] for k in scenarios]
    redis_avg = [data[k]["redis"]["avg"] for k in scenarios]
    labels = [LABELS[k] for k in scenarios]

    x = range(len(scenarios))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars1 = ax.bar([i - width / 2 for i in x], mongo_avg, width, label="MongoDB (DB goc)", color="#dc3545")
    bars2 = ax.bar([i + width / 2 for i in x], redis_avg, width, label="Redis (Cache)", color="#198754")

    for bars in (bars1, bars2):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f} ms",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                fontsize=9,
            )

    ax.set_ylabel("Thoi gian phan hoi trung binh (ms)")
    ax.set_title("So sanh thoi gian doc du lieu: MongoDB vs Redis Cache\n(De tai 06 - Cache-Aside Pattern)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    out1 = OUT_DIR / "bieu_do_hieu_nang.png"
    fig.savefig(out1, dpi=160)
    plt.close(fig)
    print(f"  + {out1}")

    # ---------------- Bieu do 2: phan bo (min/median/p95/max) ----------------
    fig, ax = plt.subplots(figsize=(9, 5.2))
    for offset, (source, color) in enumerate((("mongodb", "#dc3545"), ("redis", "#198754"))):
        mins = [data[k][source]["min"] for k in scenarios]
        meds = [data[k][source]["median"] for k in scenarios]
        p95 = [data[k][source]["p95"] for k in scenarios]
        maxs = [data[k][source]["max"] for k in scenarios]
        xs = [i + (offset - 0.5) * 0.28 for i in range(len(scenarios))]
        ax.bar(xs, maxs, 0.26, color=color, alpha=0.25, label=f"{source.upper()} - max")
        ax.bar(xs, p95, 0.26, color=color, alpha=0.5, label=f"{source.upper()} - p95")
        ax.bar(xs, meds, 0.26, color=color, alpha=0.8, label=f"{source.upper()} - median")
        ax.bar(xs, mins, 0.26, color=color, label=f"{source.upper()} - min")

    ax.set_xticks(list(range(len(scenarios))))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Thoi gian (ms)")
    ax.set_title("Phan bo thoi gian phan hoi (min / median / p95 / max)")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    out2 = OUT_DIR / "bieu_do_phan_bo.png"
    fig.savefig(out2, dpi=160)
    plt.close(fig)
    print(f"  + {out2}")

    # ---------------- Bang so sanh (copy vao Word) ----------------
    lines = [
        "| Kich ban | MongoDB (ms) | Redis (ms) | Redis nhanh hon |",
        "|---|---|---|---|",
    ]
    for k in scenarios:
        m = data[k]["mongodb"]["avg"]
        c = data[k]["redis"]["avg"]
        lines.append(f"| {LABELS[k]} | {m:.3f} | {c:.3f} | x{(m / c if c else 0):.1f} |")
    table = OUT_DIR / "bang_so_sanh.md"
    table.write_text("\n".join(lines), encoding="utf-8")
    print(f"  + {table}")


if __name__ == "__main__":
    main()
