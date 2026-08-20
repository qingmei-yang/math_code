# -*- coding: utf-8 -*-
"""Problem A 快递公司送货策略 — 全局参数与费用模型。
数据见 data_points.py（30 点，总重 184.5 kg）。"""

# ========= 通用参数 =========
WAREHOUSE = (0.0, 0.0)       # 公司总部位于坐标原点
SERVICE_TIME = 10 / 60       # 每个送货点停留 10 分钟（小时）
WEIGHT_LIMIT = 25.0          # 每次出发最多携带 25 kg
TOTAL_WEIGHT = 184.5         # 日均总重量（校验用）

# 距离：题目要求"路线为平行于坐标轴的折线" → 用曼哈顿距离
DISTANCE = "manhattan"

# ---- 第一问 / 第三问 参数 ----
SPEED = 25.0                 # 途中速度 km/h
WORK_TIME_Q1 = 6.0           # Q1：每个业务员每天工作 ≤ 6 小时
WORK_TIME_Q3 = 8.0           # Q3：可延长到 8 小时

# ---- 第二问 费用模型 ----
# 载货段：速度 20 km/h，酬金 3 元/(km·kg)
# 空载段：速度 30 km/h，酬金 2 元/km
SPEED_LOADED = 20.0
SPEED_EMPTY = 30.0
FEE_LOADED = 3.0             # 元/(km·kg)
FEE_EMPTY = 2.0              # 元/km

# ========= 30 个送货点（来自题目数据表）=========
from data_points import POINTS  # noqa: E402
