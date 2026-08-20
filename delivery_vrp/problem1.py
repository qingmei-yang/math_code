# -*- coding: utf-8 -*-
"""第一问：合理送货策略。
模型：每个业务员一天可跑多趟（每趟从总部出发、载重≤25kg、回到总部），
      业务员当天总工作时间≤6h。先"分趟"再"打包"，最小化业务员数。
分趟：最远点优先 + MOVE/SWAP（目标=组数惩罚+路程，尽量少趟）。
打包：FFD bin-packing（每业务员≤6h）。
输出：业务员数、每人运行线路、总运行公里数。"""
import os
import config as C
from utils import group_q1, feasible_q1, farthest_first, pack_workers
from optimizer import local_search
from plot_vrp import plot_groups

PENALTY = 1000.0  # 每组固定开销，驱动合并、减少趟数（从而减少业务员）


def make_trips():
    """分趟：最远点优先 + 局部优化。返回 trips [{group,dist,time,seq}]。"""
    wh = C.WAREHOUSE
    feasible = lambda g: feasible_q1(g, wh, C.WORK_TIME_Q1)   # 单趟≤6h + 载重≤25kg
    cost = lambda g: (PENALTY + group_q1(wh, g)[0]) if g else 0.0
    groups = farthest_first(wh, C.POINTS, feasible)
    groups = local_search(groups, cost, feasible, verbose=True)
    trips = []
    for g in groups:
        d, t, seq = group_q1(wh, g)
        trips.append({"group": g, "dist": d, "time": t, "seq": seq})
    return trips


def worker_route(worker):
    parts = ["总部→" + "→".join(str(p["id"]) for p in t["seq"]) + "→总部" for t in worker]
    return " ｜ ".join(parts)


def main():
    trips = make_trips()
    workers = pack_workers(trips, C.WORK_TIME_Q1)
    total_dist = sum(t["dist"] for t in trips)

    print("=" * 74)
    print("第一问：送货策略（分趟 + 业务员打包，每人可跑多趟）")
    print(f"约束：每趟载重≤{C.WEIGHT_LIMIT}kg  单趟与日工作≤{C.WORK_TIME_Q1}h  "
          f"速度{C.SPEED}km/h  曼哈顿距离")
    print("=" * 74)
    print(f"共 {len(trips)} 趟 → 打包为 {len(workers)} 名业务员 | 总运行公里数 {total_dist:.2f} km")
    print("-" * 74)
    for wi, worker in enumerate(workers, 1):
        wtime = sum(t["time"] for t in worker)
        wdist = sum(t["dist"] for t in worker)
        allpts = [p["id"] for t in worker for p in t["group"]]
        print(f"业务员{wi}：{len(worker)}趟  点{allpts}  时间{wtime:.2f}h  路程{wdist:.2f}km")
        print(f"    线路: {worker_route(worker)}")
    print("=" * 74)

    here = os.path.dirname(os.path.abspath(__file__))
    plot_groups([t["group"] for t in trips], C.WAREHOUSE,
                os.path.join(here, "results", "q1_strategy.png"),
                f"第一问：{len(trips)}趟 / {len(workers)}名业务员")
    print("路线图: results/q1_strategy.png")
    return trips, workers


if __name__ == "__main__":
    main()
