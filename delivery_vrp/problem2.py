# -*- coding: utf-8 -*-
"""第二问：费用最省策略。
载货段 20km/h、酬金 3 元/(km·kg)；空载段 30km/h、酬金 2 元/km。
分趟：多初始方案(最远点优先 / 节约算法) → MOVE/SWAP(目标=费用) → 取最优。
打包：FFD(6h) 给出业务员数。总费用 = Σ 各趟费用（与打包无关）。"""
import os
import config as C
from utils import (group_q2, feasible_q2, clarke_wright, farthest_first, pack_workers)
from optimizer import local_search, total_cost
from plot_vrp import plot_groups


def main():
    wh = C.WAREHOUSE
    work = C.WORK_TIME_Q1
    feasible = lambda g: feasible_q2(g, wh, work)
    cost_fn = lambda g: group_q2(wh, g)["cost"] if g else 0.0

    candidates = {
        "A. 最远点优先": farthest_first(wh, C.POINTS, feasible),
        "B. 节约算法": clarke_wright(wh, C.POINTS, feasible),
    }
    print("=" * 74)
    print("第二问：费用最省（载货 3元/(km·kg) + 空载 2元/km）")
    print("=" * 74)
    results = {}
    for name, g in candidates.items():
        init = total_cost(g, cost_fn)
        opt = local_search(g, cost_fn, feasible, verbose=True)
        results[name] = opt
        print(f"[{name}] 初始 {init:.1f} → 优化 {total_cost(opt, cost_fn):.1f}")

    best_name = min(results, key=lambda k: total_cost(results[k], cost_fn))
    best = results[best_name]

    trips = []
    for g in best:
        m = group_q2(wh, g)
        trips.append({"group": g, "seq": m["seq"], "time": m["time"],
                      "cost": m["cost"], "weight": m["weight"]})
    workers = pack_workers(trips, work)
    grand = sum(t["cost"] for t in trips)

    print("\n" + "=" * 74)
    print(f"★ 最优：{best_name} | {len(trips)}趟 → {len(workers)}名业务员 | 总费用 {grand:.1f} 元")
    print("=" * 74)
    for wi, worker in enumerate(workers, 1):
        wtime = sum(t["time"] for t in worker)
        wcost = sum(t["cost"] for t in worker)
        allpts = [p["id"] for t in worker for p in t["group"]]
        print(f"业务员{wi}：点{allpts}  时间{wtime:.2f}h  费用{wcost:.1f}")
        parts = ["总部→" + "→".join(str(p["id"]) for p in t["seq"]) + "→总部(空载)"
                 for t in worker]
        print(f"    线路: " + " ｜ ".join(parts))
    print("=" * 74)

    here = os.path.dirname(os.path.abspath(__file__))
    plot_groups([t["group"] for t in trips], wh,
                os.path.join(here, "results", "q2_cost.png"),
                f"第二问：费用最省 {grand:.0f}元")
    print("路线图: results/q2_cost.png")


if __name__ == "__main__":
    main()
