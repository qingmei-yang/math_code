# -*- coding: utf-8 -*-
"""局部搜索优化器：MOVE / SWAP 邻域，最小化任意目标（路程 or 费用）。
cost_fn(group)->float 与 feasible_fn(group)->bool 由调用方提供（适配 Q1/Q2）。"""


def total_cost(groups, cost_fn):
    return sum(cost_fn(g) for g in groups if g)


def local_search(groups, cost_fn, feasible_fn, max_iter=200, verbose=False):
    """best-improvement 局部搜索。每轮在 MOVE、SWAP 中各取最优一步。"""
    groups = [list(g) for g in groups if g]
    it = 0
    improved = True
    while improved and it < max_iter:
        improved = False
        it += 1

        # ---- MOVE：把点从组 i 移到组 j（不产生空组）----
        best_delta, best_move = -1e-9, None
        for i in range(len(groups)):
            if not groups[i]:
                continue  # 空组跳过（允许把单点组移空以减少组数）
            ci = cost_fn(groups[i])
            for idx, p in enumerate(groups[i]):
                new_i = groups[i][:idx] + groups[i][idx + 1:]
                for j in range(len(groups)):
                    if j == i:
                        continue
                    new_j = groups[j] + [p]
                    if not feasible_fn(new_i) or not feasible_fn(new_j):
                        continue
                    delta = (cost_fn(new_i) + cost_fn(new_j)
                             - ci - cost_fn(groups[j]))
                    if delta < best_delta:
                        best_delta, best_move = delta, (i, j, new_i, new_j)
        if best_move is not None:
            i, j, new_i, new_j = best_move
            groups[i], groups[j] = new_i, new_j
            improved = True

        # ---- SWAP：组 i 的 pa 与组 j 的 pb 互换 ----
        best_delta, best_swap = -1e-9, None
        for i in range(len(groups)):
            ci = cost_fn(groups[i])
            for j in range(i + 1, len(groups)):
                cj = cost_fn(groups[j])
                for pa in groups[i]:
                    for pb in groups[j]:
                        new_i = [pb if q["id"] == pa["id"] else q for q in groups[i]]
                        new_j = [pa if q["id"] == pb["id"] else q for q in groups[j]]
                        if not feasible_fn(new_i) or not feasible_fn(new_j):
                            continue
                        delta = cost_fn(new_i) + cost_fn(new_j) - ci - cj
                        if delta < best_delta:
                            best_delta, best_swap = delta, (i, j, new_i, new_j)
        if best_swap is not None:
            i, j, new_i, new_j = best_swap
            groups[i], groups[j] = new_i, new_j
            improved = True

    if verbose:
        print(f"  (局部搜索迭代 {it} 轮)")
    return [g for g in groups if g]
