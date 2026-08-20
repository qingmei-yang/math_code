# -*- coding: utf-8 -*-
"""第二问：五城市（深圳/广州/杭州/厦门/苏州）人才吸引力对比。
同一套权重 → 各城综合得分 → 排名表（csv）+ 雷达图（png）。"""
import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config as C
from data import DATA
from compute import compute_all, ranking

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))


def export_csv(dim, comp, rank):
    path = os.path.join(HERE, "results", "scores.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["城市", "综合得分", "排名"]
                    + [dn for dn, _, _ in C.DIMENSIONS])
        for c, s, r in rank:
            wr.writerow([c, f"{s:.4f}", r]
                        + [f"{dim[c][dn]:.4f}" for dn, _, _ in C.DIMENSIONS])
    return path


def radar(dim):
    """五城四维度雷达图。城市颜色固定（config.CITY_COLORS），不随排名变化。"""
    labels = [dn for dn, _, _ in C.DIMENSIONS]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]                      # 闭合

    fig, ax = plt.subplots(figsize=(8, 8),
                           subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)            # 第一轴朝上
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([f"{dn}\n({w:.0%})" for dn, w, _ in C.DIMENSIONS],
                       fontsize=12, color="#333333")
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"],
                       fontsize=8, color="#999999")
    ax.grid(color="#dddddd", linewidth=0.8)   # 退后的网格
    ax.spines["polar"].set_color("#dddddd")

    for city in C.CITY_ORDER:
        vals = [dim[city][dn] for dn in labels]
        vals += vals[:1]
        lw = 2.6 if city == "深圳" else 1.8   # 深圳为主对象加粗
        ax.plot(angles, vals, linewidth=lw, color=C.CITY_COLORS[city],
                label=city, zorder=3 if city == "深圳" else 2)
        ax.fill(angles, vals, color=C.CITY_COLORS[city], alpha=0.05)

    ax.set_title("五城市人才吸引力雷达图（维度得分 0–1）",
                 fontsize=14, color="#222222", pad=28)
    ax.legend(loc="upper right", bbox_to_anchor=(1.22, 1.10), fontsize=10,
              frameon=False)
    path = os.path.join(HERE, "results", "radar.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def main():
    norm, dim, comp = compute_all()
    rank = ranking(comp)

    print("=" * 66)
    print("第二问：五城市人才吸引力综合得分与排名")
    print("=" * 66)
    print(f"\n{'排名':<4}{'城市':<6}{'综合得分':<10}", end="")
    print("".join(f"{dn:<10}" for dn, _, _ in C.DIMENSIONS))
    print("-" * 66)
    for c, s, r in rank:
        line = f"{r:<4}{c:<6}{s:<10.4f}"
        line += "".join(f"{dim[c][dn]:<10.3f}" for dn, _, _ in C.DIMENSIONS)
        print(line)
    print("-" * 66)

    csv_path = export_csv(dim, comp, rank)
    png_path = radar(dim)
    print(f"\n排名表已导出: {csv_path}")
    print(f"雷达图已导出: {png_path}")

    # 简要点评（供论文手参考）
    top = rank[0][0]
    sz = next(x for x in rank if x[0] == "深圳")
    print(f"\n要点：{top}居首（{rank[0][1]:.3f}）；深圳第{sz[2]}名（{sz[1]:.3f}）")
    for dn, w, inds in C.DIMENSIONS:
        vals = {c: dim[c][dn] for c in C.CITY_ORDER}
        best = max(vals, key=vals.get)
        worst = min(vals, key=vals.get)
        print(f"  {dn}: 最强 {best}({vals[best]:.2f}) / 最弱 {worst}({vals[worst]:.2f})")


if __name__ == "__main__":
    main()
