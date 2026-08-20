# -*- coding: utf-8 -*-
"""第三问：工作时间 6h → 8h 的策略变化。
分趟一致（载重≤25kg、单趟≤6h），只改业务员打包上限：6h vs 8h。
8h 能让每名业务员塞进更多趟 → 业务员数下降。"""
import os
import config as C
from utils import pack_workers
from problem1 import make_trips
from plot_vrp import plot_groups


def main():
    trips = make_trips()                       # 分趟（两问共用）
    w6 = pack_workers(trips, C.WORK_TIME_Q1)   # 6h 打包
    w8 = pack_workers(trips, C.WORK_TIME_Q3)   # 8h 打包
    total_dist = sum(t["dist"] for t in trips)

    print("=" * 74)
    print("第三问：工作时间 6h → 8h 的策略变化")
    print(f"(共 {len(trips)} 趟，总路程 {total_dist:.2f} km 不变；仅业务员打包变化)")
    print("=" * 74)
    print(f"  6 小时打包：{len(w6)} 名业务员")
    print(f"  8 小时打包：{len(w8)} 名业务员")
    print("-" * 74)
    print("【8 小时方案】")
    for wi, worker in enumerate(w8, 1):
        wtime = sum(t["time"] for t in worker)
        allpts = [p["id"] for t in worker for p in t["group"]]
        parts = ["总部→" + "→".join(str(p["id"]) for p in t["seq"]) + "→总部"
                 for t in worker]
        print(f"业务员{wi}：{len(worker)}趟  点{allpts}  时间{wtime:.2f}h")
        print(f"    线路: " + " ｜ ".join(parts))
    dn = len(w6) - len(w8)
    print("-" * 74)
    print(f"变化：业务员 {'减少' if dn > 0 else '增加' if dn < 0 else '不变'} {abs(dn)} 名"
          f"（{len(w6)} → {len(w8)}）")
    print("=" * 74)

    here = os.path.dirname(os.path.abspath(__file__))
    plot_groups([t["group"] for t in trips], C.WAREHOUSE,
                os.path.join(here, "results", "q3_8h.png"),
                f"第三问：8h 打包 → {len(w8)}名业务员")
    print("路线图: results/q3_8h.png")


if __name__ == "__main__":
    main()
