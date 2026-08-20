# -*- coding: utf-8 -*-
"""核心计算：Min-Max 归一化（负向反向）→ 维度得分 → 加权综合得分。
归一化标尺 = 五城市同指标 min/max（单城市无法定义 min-max，
与第二问'同一年份、口径一致'的要求对齐）。"""
import config as C
from data import DATA


def all_indicators():
    """返回指标名列表（按 DIMENSIONS 顺序展开）。"""
    return [ind for _, _, inds in C.DIMENSIONS for ind in inds]


def normalize(value, values, negative):
    """Min-Max 归一化到 0-1；负向指标反向（值越大得分越低）。"""
    mn, mx = min(values), max(values)
    if abs(mx - mn) < 1e-12:
        return 1.0
    return (mx - value) / (mx - mn) if negative else (value - mn) / (mx - mn)


def compute_all():
    """返回 (归一化矩阵, 维度得分, 综合得分)。
    norm[城市][指标] = 0-1；dim[城市][维度] = 0-1；comp[城市] = 0-1。"""
    cities = C.CITY_ORDER
    # 1) 归一化
    norm = {c: {} for c in cities}
    for ind in all_indicators():
        vals = DATA[ind]
        for c in cities:
            norm[c][ind] = normalize(vals[c], list(vals.values()), ind in C.NEGATIVE)
    # 2) 维度得分（维度内子权重均分或自定义）
    dim = {c: {} for c in cities}
    for dname, _, inds in C.DIMENSIONS:
        if C.SUB_WEIGHT and dname in C.SUB_WEIGHT:
            w = C.SUB_WEIGHT[dname]
        else:
            w = [1.0 / len(inds)] * len(inds)
        for c in cities:
            dim[c][dname] = sum(norm[c][i] * wi for i, wi in zip(inds, w))
    # 3) 综合得分
    comp = {c: sum(dw * dim[c][dn] for dn, dw, _ in C.DIMENSIONS) for c in cities}
    return norm, dim, comp


def ranking(comp):
    """按综合得分降序排名，返回 [(城市, 得分, 名次), ...]。"""
    order = sorted(C.CITY_ORDER, key=lambda c: -comp[c])
    return [(c, comp[c], r) for r, c in enumerate(order, 1)]
