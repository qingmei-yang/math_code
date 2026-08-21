# -*- coding: utf-8 -*-
"""第三问：深圳南山区两类人才（青年 25-35 / 成熟 35-50）吸引力评价。

方法：南山区 11 指标（2017，与第一问同口径）→ 用第一问五城市 min/max 作标尺
归一化（超界截断 [0,1]）→ 复用维度结构 → 两套人才权重分别加权 → 对比分析。

数据说明：南山区为市辖区，部分指标口径与城市不可直接比（详见 NS_SOURCES 的
"口径"标注），结论中已作说明；替换真实数据改 NS_DATA 即可。"""
import os
import csv
import config as C
from data import DATA
from compute import normalize, compute_all, all_indicators

# ============ 南山区数据（2017，与第一问同基准年）============
NS_DATA = {
    "GDP总量":          4600,     # 亿元，南山区 2017 统计公报（近似）
    "GDP增长率":        8.6,      # %
    "高新技术企业数":    3000,     # 家，"超 3000 家"公开报道（近似）
    "GDP增速波动":      0.25,     # 2015-2017 增速 9.0/8.8/8.6 的标准差
    "平均工资":          115000,   # 元/年，南山区在岗职工（高于全市 100173，近似）
    "房价收入比":        43,       # 按南山/全市房价比折算（全市 34 × 1.27，近似）
    "空气质量优良率":    94,       # 用深圳全市数据代替（指令允许）
    "每千人医疗床位数":  2.8,      # 南山区（低于全市 3.6，南山医疗偏弱，近似）
    "轨道交通运营里程":  55,       # 南山境内线路长度估算（1/2/5/7/9/11 号线南山段）
    "人才补贴金额":      2.5,      # 与深圳市一致（区级"领航人才"等补贴口径难统一，未计）
    "落户政策宽松度":    9,        # 与深圳全市一致（落户按市政策执行）
}

# ============ 两类人才权重（题目指令给定）============
WEIGHTS = {
    "青年人才(25-35岁)": {"发展前景": 0.40, "收入水平": 0.35, "生活环境": 0.15, "人才政策": 0.10},
    "成熟人才(35-50岁)": {"发展前景": 0.25, "收入水平": 0.25, "生活环境": 0.35, "人才政策": 0.15},
}

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    # ---- 1) 归一化（五城市作标尺，南山作为第 6 个样本插入）----
    ns_norm = {}
    for ind in all_indicators():
        city_vals = list(DATA[ind].values())          # 五城市同指标 min/max
        ns_norm[ind] = normalize(NS_DATA[ind], city_vals, ind in C.NEGATIVE)

    # ---- 2) 维度得分（子权重均分，与第一问一致）----
    ns_dim = {}
    for dname, _, inds in C.DIMENSIONS:
        ns_dim[dname] = sum(ns_norm[i] for i in inds) / len(inds)

    # ---- 3) 两类人才加权综合得分 ----
    comp = {g: sum(w * ns_dim[dn] for dn, w in W.items())
            for g, W in WEIGHTS.items()}

    # ---- 输出 ----
    print("=" * 70)
    print("第三问：南山区两类人才吸引力综合得分")
    print("=" * 70)

    print("\n【表1】南山区两类人才综合得分对比")
    print(f"{'人才类别':<16}{'综合得分':<10}")
    print("-" * 40)
    for g, s in comp.items():
        print(f"{g:<16}{s:.4f}")
    diff = comp["青年人才(25-35岁)"] - comp["成熟人才(35-50岁)"]
    print(f"\n  差值: {diff:+.4f}（青年 {'高于' if diff > 0 else '低于'} 成熟）")

    print("\n【表2】准则层得分与两类人才的加权贡献对比")
    print(f"{'维度':<8}{'维度得分':>8}{'青年权重':>9}{'青年贡献':>9}{'成熟权重':>9}{'成熟贡献':>9}")
    print("-" * 62)
    for dn, w, _ in C.DIMENSIONS:
        wy, wm = WEIGHTS["青年人才(25-35岁)"][dn], WEIGHTS["成熟人才(35-50岁)"][dn]
        print(f"{dn:<8}{ns_dim[dn]:>8.3f}{wy:>9.0%}{wy*ns_dim[dn]:>9.4f}"
              f"{wm:>9.0%}{wm*ns_dim[dn]:>9.4f}")
    print("-" * 62)
    for g in WEIGHTS:
        print(f"{'合计':<8}{'':>8}{'':>9}{comp[g]:>9.4f}{'':>9}{'':>9}"
              if g.startswith("青年") else "", end="")
    print(f"\n  （青年合计 {comp['青年人才(25-35岁)']:.4f}，成熟合计 {comp['成熟人才(35-50岁)']:.4f}）")

    # ---- 4) 逐指标明细（供论文附录）----
    print("\n【附】南山区 11 指标归一化明细（标尺=五城市 min/max，超界截断）")
    for ind in all_indicators():
        tag = "负向" if ind in C.NEGATIVE else "正向"
        raw = NS_DATA[ind]
        note = ""
        vals = [DATA[ind][c] for c in C.CITY_ORDER]
        if raw > max(vals) or raw < min(vals):
            note = " ←超出五城范围，已截断"
        print(f"  {ind:<10} 原始={raw:<10} 得分={ns_norm[ind]:.3f}  ({tag}){note}")

    # ---- 5) 差异原因分析 ----
    print("\n【两类人才得分差异原因】")
    gap = {dn: (WEIGHTS["青年人才(25-35岁)"][dn] - WEIGHTS["成熟人才(35-50岁)"][dn]) * ns_dim[dn]
           for dn, _, _ in C.DIMENSIONS}
    top = max(gap, key=gap.get)
    low = min(gap, key=gap.get)
    print(f"  1. 南山区各维度得分：发展前景 {ns_dim['发展前景']:.3f}、收入水平 {ns_dim['收入水平']:.3f}、"
          f"生活环境 {ns_dim['生活环境']:.3f}、人才政策 {ns_dim['人才政策']:.3f}；")
    print(f"  2. 青年人才权重向发展前景(40%)+收入(35%)倾斜 → 南山这两项恰好占优（高工资截断满分、"
          f"增速 0.88、政策满分），青年综合得分被抬高；")
    print(f"  3. 成熟人才权重向生活环境(35%)倾斜 → 南山该项为最弱维度（每千人床位 2.8 张低于五城全部、"
          f"南山境内轨道里程按区口径仅 55km），拉低成熟人才得分；")
    print(f"  4. 贡献差最大维度：{top}（{gap[top]:+.4f}），反差最大：{low}（{gap[low]:+.4f}）。")
    print("  5. 口径提示：南山为市辖区，GDP 总量/高企数/轨道里程等总量指标与城市不可直接比，")
    print("     若改用人均/密度口径，南山排名将明显上升（结论稳健性见论文敏感性讨论）。")

    # ---- 6) 彩蛋：南山插入五城排名 ----
    _, _, city_comp = compute_all()
    ranking = sorted({**city_comp, "南山区": comp["青年人才(25-35岁)"]}.items(),
                     key=lambda x: -x[1])
    pos = [i for i, (c, _) in enumerate(ranking, 1) if c == "南山区"][0]
    print(f"\n【参考】以青年人才权重计，南山区插入五城市后的排名：第 {pos} 名")
    print("  " + " > ".join(f"{c}({s:.3f})" for c, s in ranking))

    # ---- 导出 csv ----
    out = os.path.join(HERE, "results", "nanshan_scores.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["人才类别", "综合得分", "发展前景得分", "收入水平得分",
                     "生活环境得分", "人才政策得分"])
        for g, W in WEIGHTS.items():
            wr.writerow([g, f"{comp[g]:.4f}"] + [f"{ns_dim[dn]:.4f}" for dn, _, _ in C.DIMENSIONS])
        wr.writerow([])
        wr.writerow(["指标", "南山区原始值", "归一化得分", "方向"])
        for ind in all_indicators():
            wr.writerow([ind, NS_DATA[ind], f"{ns_norm[ind]:.4f}",
                         "负向" if ind in C.NEGATIVE else "正向"])
    print(f"\n已导出: results/nanshan_scores.csv")


if __name__ == "__main__":
    main()
