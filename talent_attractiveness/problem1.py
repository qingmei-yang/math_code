# -*- coding: utf-8 -*-
"""第一问：深圳市人才吸引力综合得分（0-1）。
方法：11 指标 Min-Max 归一化（负向反向：房价收入比、GDP增速波动）
      → 4 维度（35%/30%/20%/15%）加权求和。
说明：Min-Max 需要多城截面作标尺，此处用五城（与第二问同口径），
      因此第一问输出与第二问排名表完全一致、可直接衔接。"""
import config as C
from data import DATA, SOURCES
from compute import compute_all, all_indicators


def main():
    norm, dim, comp = compute_all()

    print("=" * 66)
    print("第一问：深圳市人才吸引力综合得分")
    print("=" * 66)

    print("\n【深圳 11 项指标原始值与归一化】")
    print(f"{'指标':<10}{'原始值':>12}{'归一化':>8}   性质")
    for ind in all_indicators():
        raw = DATA[ind]["深圳"]
        nv = norm["深圳"][ind]
        tag = "负向" if ind in C.NEGATIVE else "正向"
        print(f"{ind:<10}{raw:>12}{nv:>8.3f}   {tag} [{SOURCES[ind]['nature']}]")

    print("\n【维度得分（维度内子权重均分）】")
    for dname, w, inds in C.DIMENSIONS:
        print(f"  {dname}（权重 {w:.0%}，含 {len(inds)} 项指标）: "
              f"{dim['深圳'][dname]:.3f}")

    print("\n【综合得分】")
    detail = " + ".join(f"{w:.0%}×{dim['深圳'][dn]:.3f}"
                        for dn, w, _ in C.DIMENSIONS)
    print(f"  深圳 = {detail} = {comp['深圳']:.3f}")

    print("\n说明：")
    print("  · 负向指标（房价收入比、GDP增速波动）已反向归一化")
    print("  · 'GDP增速波动'由 2015–2017 三年增速标准差计算（对应'近3年'）")
    print("  · 其余指标为 2017 年截面数据，来源与性质见 data.py 的 SOURCES")
    print("=" * 66)


if __name__ == "__main__":
    main()
