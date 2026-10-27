"""Vẽ kết quả schema v2: số đo thật tách khỏi mô phỏng, giữ phân bố mẫu thô."""
import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULT_FILE = ROOT / "data" / "result_benchmark.json"
OUT_DIR = ROOT / "docs" / "figures"
COLORS = {"mongodb": "#d94841", "redis": "#16865b"}


def bar_chart(axis, keys, scenarios, title):
    for offset, source in ((-.18, "mongodb"), (.18, "redis")):
        values = [scenarios[key][source]["avg"] for key in keys]
        bars = axis.bar([i + offset for i in range(len(keys))], values, .34,
                        label="DB / MISS" if source == "mongodb" else "Redis / HIT", color=COLORS[source])
        axis.bar_label(bars, labels=[f"{value:.3f}" for value in values], padding=4, fontsize=9)
    axis.set_xticks(range(len(keys)), ["Chi tiết bài" if key == "article_detail" else "Danh sách 9 bài" if key == "article_list" else "HTTP request" for key in keys])
    axis.set_ylabel("Thời gian trung bình (ms)")
    axis.set_title(title)
    axis.grid(axis="y", alpha=.2)
    axis.set_axisbelow(True)
    axis.margins(y=.25)
    axis.legend()


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=RESULT_FILE)
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    if data.get("schema_version") != 2:
        raise ValueError("Cần chạy benchmark.py mới trước khi vẽ; không dùng số liệu cũ sai phương pháp.")
    args.out.mkdir(parents=True, exist_ok=True)
    scenarios = data["scenarios"]
    raw = [key for key, value in scenarios.items() if value["layer"] == "data"]
    http = [key for key, value in scenarios.items() if value["layer"] == "http" and value["simulated_db_latency_ms"] == 0]
    env = data["environment"]
    fig, axes = plt.subplots(1, 2 if http else 1, figsize=(12 if http else 7, 5.2), squeeze=False)
    bar_chart(axes[0, 0], raw, scenarios, "Đọc và chuyển đổi cùng payload")
    if http:
        bar_chart(axes[0, 1], http, scenarios, "HTTP: cùng nội dung, kiểm tra source")
    fig.suptitle(f"Số đo thực tế cục bộ — {env['n_per_source']} mẫu/nguồn, {env['warmup_per_source']} warm-up", fontsize=13)
    fig.text(.5, .015, "Hai biểu đồ có thang đo riêng. Chuẩn bị/xóa cache và kiểm tra payload nằm ngoài đồng hồ đo.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .045, 1, .94))
    fig.savefig(args.out / "bieu_do_hieu_nang.png", dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2 if http else 1, figsize=(12 if http else 7, 5.2), squeeze=False)
    for axis, group, title in [(axes[0, 0], raw, "Lớp dữ liệu")]+([(axes[0, 1], http, "HTTP request")] if http else []):
        samples, labels, colors = [], [], []
        for key in group:
            for source in ("mongodb", "redis"):
                samples.append(data["samples_ms"][key][source])
                short = "Chi tiết" if key == "article_detail" else "Danh sách" if key == "article_list" else "HTTP"
                labels.append(short + "\n" + ("DB/MISS" if source == "mongodb" else "Redis/HIT"))
                colors.append(COLORS[source])
        box = axis.boxplot(samples, tick_labels=labels, patch_artist=True, showfliers=True)
        for patch, color in zip(box["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(.5)
        axis.set_ylabel("Thời gian (ms)")
        axis.set_title(title)
        axis.grid(axis="y", alpha=.2)
    fig.suptitle("Phân bố mẫu đo thật — giữ cả các điểm ngoại lệ", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, .93))
    fig.savefig(args.out / "bieu_do_phan_bo.png", dpi=170)
    plt.close(fig)

    simulated = [key for key, value in scenarios.items() if value["simulated_db_latency_ms"] > 0]
    if simulated:
        fig, axis = plt.subplots(figsize=(8, 4.5))
        bar_chart(axis, simulated, scenarios, "MÔ PHỎNG — không phải số đo mạng thực tế")
        axis.set_xticks(range(len(simulated)), [scenarios[key]["label"] for key in simulated])
        fig.tight_layout()
        fig.savefig(args.out / "bieu_do_mo_phong.png", dpi=170)
        plt.close(fig)

    lines = ["# Kết quả benchmark đã đo lại", "", f"Thời điểm: {data['recorded_at']}", "",
             f"Mỗi nguồn: {env['n_per_source']} mẫu, {env['warmup_per_source']} warm-up. p95: nearest-rank.", "",
             "| Kịch bản | DB/MISS TB (ms) | Redis/HIT TB (ms) | DB/MISS p95 (ms) | Redis/HIT p95 (ms) | Tỷ số TB DB/Redis |",
             "|---|---:|---:|---:|---:|---:|"]
    for key, value in scenarios.items():
        left, right = value["mongodb"], value["redis"]
        lines.append(f"| {value['label']} | {left['avg']:.3f} | {right['avg']:.3f} | {left['p95']:.3f} | {right['p95']:.3f} | {left['avg']/max(right['avg'],1e-9):.2f}× |")
    lines += ["", "Mô phỏng được ghi rõ từng dòng và vẽ riêng. HTTP gồm request + giải mã JSON; không đồng nhất với thời gian một lệnh Redis.",
              "", "Không có dòng cache tìm kiếm: chức năng tìm kiếm gần đúng hiện không cache kết quả trong app.",
              "", "Nguồn: data/result_benchmark.json và CSV cùng tên chứa các mẫu thô. Xem docs/PERFORMANCE_REPORT.md để biết phương pháp và giới hạn."]
    (args.out / "bang_so_sanh.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"Đã cập nhật biểu đồ và bảng trong {args.out}")


if __name__ == "__main__":
    main()
