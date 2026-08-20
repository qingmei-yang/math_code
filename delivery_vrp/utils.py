# -*- coding: utf-8 -*-
"""核心工具：曼哈顿距离、组内路线规划(最近邻+2-opt)、Q1/Q3 与 Q2 的时间/费用、
最远点优先分组、业务员打包(FFD)。

题目关键设定：
- 总部在坐标原点，路线为"平行于坐标轴的折线" → 距离用曼哈顿距离
- Q1/Q3：统一速度 25 km/h；时间 = 距离/25 + 每点10分钟
- Q2：载货 20 km/h、3 元/(km·kg)；空载 30 km/h、2 元/km
- 一个业务员一天可跑多趟，总工作时间≤6h（Q3 为 8h）
"""
import config as C


def coord(p):
    return (p["x"], p["y"])


def manhattan(a, b):
    """曼哈顿距离（折线路线）。"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def seq_distance(warehouse, seq):
    """seq 为访问顺序的点列表，返回含首尾总部的曼哈顿总距离。"""
    pts = [warehouse] + [coord(p) for p in seq] + [warehouse]
    return sum(manhattan(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def nearest_neighbor_order(warehouse, group):
    seq, unvisited, cur = [], list(group), warehouse
    while unvisited:
        nxt = min(unvisited, key=lambda p: manhattan(cur, coord(p)))
        seq.append(nxt)
        unvisited.remove(nxt)
        cur = coord(nxt)
    return seq


def two_opt_order(warehouse, seq, max_iter=200):
    best = list(seq)
    improved, it = True, 0
    while improved and it < max_iter:
        improved, it = False, it + 1
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                cand = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                if seq_distance(warehouse, cand) < seq_distance(warehouse, best) - 1e-9:
                    best, improved = cand, True
    return best


def order_group(warehouse, group):
    """对一组点求访问顺序（最近邻 + 2-opt，曼哈顿）。"""
    if not group:
        return []
    return two_opt_order(warehouse, nearest_neighbor_order(warehouse, group))


def group_weight(group):
    return sum(p["w"] for p in group)


# ============ 第一问 / 第三问：统一速度 ============
def group_q1(warehouse, group, cfg=C):
    """返回 (距离km, 时间h, 访问顺序seq)。"""
    seq = order_group(warehouse, group)
    dist = seq_distance(warehouse, seq)
    t = dist / cfg.SPEED + len(seq) * cfg.SERVICE_TIME
    return dist, t, seq


# ============ 第二问：载货/空载分速 + 重量·里程费用 ============
def group_q2(warehouse, group, cfg=C):
    """返回 dict：分载货/空载的距离、时间、费用，及访问顺序。"""
    seq = order_group(warehouse, group)
    if not seq:                       # 空组（优化过程可能产生）
        return {"seq": [], "weight": 0.0, "dist_loaded": 0.0, "dist_empty": 0.0,
                "dist_total": 0.0, "time": 0.0, "cost_loaded": 0.0,
                "cost_empty": 0.0, "cost": 0.0}
    W = sum(p["w"] for p in seq)
    pts = [warehouse] + [coord(p) for p in seq]
    dist_loaded, cost_loaded, load = 0.0, 0.0, W
    for i in range(len(pts) - 1):
        seg = manhattan(pts[i], pts[i + 1])
        dist_loaded += seg
        cost_loaded += cfg.FEE_LOADED * seg * load      # 3 元/(km·kg)
        load -= seq[i]["w"]                              # 到达 seq[i] 后卸货
    dist_empty = manhattan(coord(seq[-1]), warehouse)
    cost_empty = cfg.FEE_EMPTY * dist_empty              # 2 元/km
    time_total = (dist_loaded / cfg.SPEED_LOADED
                  + dist_empty / cfg.SPEED_EMPTY
                  + len(seq) * cfg.SERVICE_TIME)
    return {
        "seq": seq, "weight": W,
        "dist_loaded": dist_loaded, "dist_empty": dist_empty,
        "dist_total": dist_loaded + dist_empty,
        "time": time_total,
        "cost_loaded": cost_loaded, "cost_empty": cost_empty,
        "cost": cost_loaded + cost_empty,
    }


def feasible_q1(group, warehouse, work_time, cfg=C):
    if group_weight(group) > cfg.WEIGHT_LIMIT:
        return False
    _, t, _ = group_q1(warehouse, group, cfg)
    return t <= work_time + 1e-9


def feasible_q2(group, warehouse, work_time, cfg=C):
    if group_weight(group) > cfg.WEIGHT_LIMIT:
        return False
    return group_q2(warehouse, group, cfg)["time"] <= work_time + 1e-9


def farthest_first(warehouse, points, feasible_fn):
    """最远点优先分组：每轮选距总部最远的未分组点作种子，就近吸收，超限则开新组。"""
    remaining = list(points)
    groups = []
    while remaining:
        seed = max(remaining, key=lambda p: manhattan(warehouse, coord(p)))
        group = [seed]
        remaining.remove(seed)
        while remaining:
            last = coord(group[-1])
            nearest = min(remaining, key=lambda p: manhattan(last, coord(p)))
            tentative = group + [nearest]
            if feasible_fn(tentative):
                group.append(nearest)
                remaining.remove(nearest)
            else:
                break
        groups.append(group)
    return groups


def clarke_wright(warehouse, points, feasible_fn):
    """节约算法分组（曼哈顿距离），feasible_fn(group)->bool 判断可行性。"""
    groups = [[p] for p in points]

    def save(pi, pj):
        return (manhattan(warehouse, coord(pi)) + manhattan(warehouse, coord(pj))
                - manhattan(coord(pi), coord(pj)))

    pairs = []
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((save(points[i], points[j]), points[i]["id"], points[j]["id"]))
    pairs.sort(reverse=True, key=lambda x: x[0])

    def find_endpoint(pid):
        for gi, g in enumerate(groups):
            if not g:
                continue
            if g[0]["id"] == pid:
                return (gi, "head")
            if g[-1]["id"] == pid:
                return (gi, "tail")
        return None

    for s, id_i, id_j in pairs:
        if s <= 0:
            break
        ei, ej = find_endpoint(id_i), find_endpoint(id_j)
        if ei is None or ej is None:
            continue
        gi, posi, gj, posj = ei[0], ei[1], ej[0], ej[1]
        if gi == gj:
            continue
        gA, gB = groups[gi][:], groups[gj][:]
        if posi == "head":
            gA = gA[::-1]
        if posj == "tail":
            gB = gB[::-1]
        merged = gA + gB
        if feasible_fn(merged):
            groups[gi] = merged
            groups[gj] = []
    return [g for g in groups if g]


def pack_workers(trips, work_time):
    """把趟按时间 FFD(First-Fit-Decreasing) 打包到业务员。
    trips: [{...,"time":...},...] → 返回 [[trip,...], ...]（每名业务员负责的趟）。"""
    ts = sorted(trips, key=lambda x: x["time"], reverse=True)
    workers = []  # [{"used":float,"trips":[...]}]
    for t in ts:
        for w in workers:
            if w["used"] + t["time"] <= work_time + 1e-9:
                w["used"] += t["time"]
                w["trips"].append(t)
                break
        else:
            workers.append({"used": t["time"], "trips": [t]})
    return [w["trips"] for w in workers]
