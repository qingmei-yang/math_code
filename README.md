# math_code · 数学建模代码仓

| 项目 | 题目 | 内容 |
|---|---|---|
| [delivery_vrp/](delivery_vrp/) | **Problem A · 快递公司送货策略** | 带载重+工时约束的 CVRP：曼哈顿距离、两阶段（分趟+FFD 打包）、三问完整解（Q1: 5人/478km；Q2: 费用最省 13800.7 元；Q3: 8h→4人） |
| [talent_attractiveness/](talent_attractiveness/) | **Problem B · 人才吸引力评价模型** | 11 指标 4 维度加权综合评价（35/30/20/15）：Min-Max 归一化（负向反向），深圳 0.713 居首；五城排名表 + 雷达图 |

## 快速运行
```bash
cd delivery_vrp            # 或 talent_attractiveness
python problem1.py         # 各问独立运行，输出结果与图表
```
依赖：Python 3.10+，matplotlib、numpy（`pip install matplotlib numpy`）
