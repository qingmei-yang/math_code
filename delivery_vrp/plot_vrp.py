# -*- coding: utf-8 -*-
"""绘图：分组路线可视化（曼哈顿顺序，存 PNG 到 results/）。"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from utils import coord, order_group

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

_COLORS = plt.get_cmap("tab10").colors


def plot_groups(groups, warehouse, save_path, title="分组路线"):
    fig, ax = plt.subplots(figsize=(11, 9))
    wx, wy = warehouse

    for gi, g in enumerate(groups):
        c = _COLORS[gi % len(_COLORS)]
        seq = order_group(warehouse, g)
        route = [warehouse] + [coord(p) for p in seq] + [warehouse]
        rx = [p[0] for p in route]
        ry = [p[1] for p in route]
        ax.plot(rx, ry, "-", color=c, linewidth=1.6, alpha=0.85, zorder=2,
                label=f"业务员{gi + 1}（{len(g)}点）")
        ax.scatter([coord(p)[0] for p in g], [coord(p)[1] for p in g],
                   color=c, s=90, zorder=3)
        for p in g:
            ax.annotate(str(p["id"]), coord(p), fontsize=8,
                        xytext=(3, 3), textcoords="offset points", zorder=4)

    ax.scatter([wx], [wy], marker="s", color="black", s=220, zorder=5)
    ax.annotate("总部(0,0)", (wx, wy), fontsize=10, fontweight="bold",
                xytext=(7, 7), textcoords="offset points", zorder=5)

    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.01, 1))
    ax.set_title(title)
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")

    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=130, bbox_inches="tight")
    plt.close()
    return save_path
