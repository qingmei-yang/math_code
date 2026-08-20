# -*- coding: utf-8 -*-
"""一键导出三问结果：生成 results_summary.md（人读）+ results.csv（Excel）。
数据由代码实时计算，与 problem1/2/3.py 运行结果完全一致。
用法：python export_results.py"""
import os
import csv
import config as C
from utils import (group_q2, feasible_q2, farthest_first, clarke_wright,
                   pack_workers, group_weight)
from optimizer import local_search
from problem1 import make_trips

HERE = os.path.dirname(os.path.abspath(__file__))


def worker_lines(worker, loaded=False):
    tag = "→总部(空载)" if loaded else "→总部"
    return " ｜ ".join("总部→" + "→".join(str(p["id"]) for p in t["seq"]) + tag
                      for t in worker)


def q1_q3():
    trips = make_trips()
    w6 = pack_workers(trips, C.WORK_TIME_Q1)
    w8 = pack_workers(trips, C.WORK_TIME_Q3)
    return trips, w6, w8, sum(t["dist"] for t in trips)


def q2():
    wh, work = C.WAREHOUSE, C.WORK_TIME_Q1
    feas = lambda g: feasible_q2(g, wh, work)
    cost = lambda g: group_q2(wh, g)["cost"] if g else 0.0
    cands = {"最远点优先": farthest_first(wh, C.POINTS, feas),
             "节约算法": clarke_wright(wh, C.POINTS, feas)}
    best, bestc = None, float("inf")
    for g in cands.values():
        opt = local_search(g, cost, feas)
        c = sum(cost(x) for x in opt if x)
        if c < bestc:
            best, bestc = opt, c
    trips = []
    for g in best:
        m = group_q2(wh, g)
        trips.append({"group": g, "seq": m["seq"], "time": m["time"],
                      "cost": m["cost"], "weight": m["weight"]})
    return trips, pack_workers(trips, work), bestc


def build_md(trips, w6, w8, total_dist, q2w, q2cost):
    L = []
    a = L.append
    a("# Problem A · 快递公司送货策略 — 结果汇总")
    a("")
    a(f"参数：总部(0,0)、曼哈顿距离、速度 {C.SPEED} km/h、"
      f"每点停 {C.SERVICE_TIME*60:.0f} min、载重≤{C.WEIGHT_LIMIT} kg、"
      f"30 点共 {C.TOTAL_WEIGHT} kg。一个业务员一天可跑多趟。")
    a("")
    a("---")
    a("")
    # Q1
    a("## 第一问（每业务员 ≤ 6h）")
    a("")
    a(f"- **业务员数：{len(w6)} 人**（{len(trips)} 趟打包而成）")
    a(f"- **总运行公里数：{total_dist:.2f} km**")
    a("")
    a("> 每趟载重 ≤ 25kg；下表「日运量」为该业务员当日各趟合计（每趟单独已 ≤25kg）。")
    a("")
    a("| 业务员 | 趟数 | 送货点 | 日运量kg | 时间h | 路程km | 线路 |")
    a("|---|---|---|---|---|---|---|")
    for i, w in enumerate(w6, 1):
        pts = [p["id"] for t in w for p in t["group"]]
        a(f"| {i} | {len(w)} | {pts} | "
          f"{sum(group_weight(t['group']) for t in w):.1f} | "
          f"{sum(t['time'] for t in w):.2f} | "
          f"{sum(t['dist'] for t in w):.2f} | {worker_lines(w)} |")
    a("")
    # Q2
    a("## 第二问（费用最省：载货 3元/(km·kg) + 空载 2元/km）")
    a("")
    a(f"- **业务员数：{len(q2w)} 人**")
    a(f"- **总费用：{q2cost:.1f} 元**")
    a("")
    a("> 每趟载重 ≤ 25kg；下表「日运量」为多趟合计，每趟单独已 ≤25kg。")
    a("")
    a("| 业务员 | 送货点 | 日运量kg | 时间h | 费用元 | 线路 |")
    a("|---|---|---|---|---|---|")
    for i, w in enumerate(q2w, 1):
        pts = [p["id"] for t in w for p in t["group"]]
        a(f"| {i} | {pts} | {sum(t['weight'] for t in w):.1f} | "
          f"{sum(t['time'] for t in w):.2f} | {sum(t['cost'] for t in w):.1f} | "
          f"{worker_lines(w, loaded=True)} |")
    a("")
    # Q3
    a("## 第三问（每业务员 ≤ 8h）")
    a("")
    a(f"- **业务员数：{len(w8)} 人**（6h 的 {len(w6)} 人 → 8h 的 {len(w8)} 人，"
      f"减少 {len(w6)-len(w8)} 人）")
    a(f"- 总运行公里数不变：{total_dist:.2f} km")
    a("")
    a("| 业务员 | 趟数 | 送货点 | 时间h | 线路 |")
    a("|---|---|---|---|---|")
    for i, w in enumerate(w8, 1):
        pts = [p["id"] for t in w for p in t["group"]]
        a(f"| {i} | {len(w)} | {pts} | {sum(t['time'] for t in w):.2f} | "
          f"{worker_lines(w)} |")
    a("")
    a("---")
    a("")
    a("*由 export_results.py 自动生成，与 problem1/2/3.py 运行结果一致。*")
    return "\n".join(L)


def build_csv(w6, w8, total_dist, q2w):
    rows = []
    for i, w in enumerate(w6, 1):
        ids = ":".join(str(p["id"]) for t in w for p in t["group"])
        rows.append(["Q1-6h", i, len(w), ids,
                     round(sum(group_weight(t["group"]) for t in w), 1),
                     round(sum(t["time"] for t in w), 2),
                     round(sum(t["dist"] for t in w), 2), ""])
    for i, w in enumerate(q2w, 1):
        ids = ":".join(str(p["id"]) for t in w for p in t["group"])
        rows.append(["Q2-费用最省", i, len(w), ids,
                     round(sum(t["weight"] for t in w), 1),
                     round(sum(t["time"] for t in w), 2), "",
                     round(sum(t["cost"] for t in w), 1)])
    for i, w in enumerate(w8, 1):
        ids = ":".join(str(p["id"]) for t in w for p in t["group"])
        rows.append(["Q3-8h", i, len(w), ids, "",
                     round(sum(t["time"] for t in w), 2), total_dist, ""])
    return rows


def main():
    trips, w6, w8, total_dist = q1_q3()
    q2trips, q2w, q2cost = q2()

    md = build_md(trips, w6, w8, total_dist, q2w, q2cost)
    with open(os.path.join(HERE, "results_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(HERE, "results.csv"), "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["问题", "业务员", "趟数", "送货点", "重量kg", "时间h", "路程km", "费用元"])
        wr.writerows(build_csv(w6, w8, total_dist, q2w))

    print("已生成: results_summary.md  和  results.csv")
    print(f"摘要：Q1 = {len(w6)}人 / {total_dist:.1f}km | "
          f"Q2 = {len(q2w)}人 / {q2cost:.1f}元 | Q3(8h) = {len(w8)}人")


if __name__ == "__main__":
    main()
