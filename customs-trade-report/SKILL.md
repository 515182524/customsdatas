---
name: customs-trade-report
description: Analyze China customs import/export tables and generate a multi-dimensional Markdown report with local SVG charts. Use when the user provides CSV/XLSX customs data or asks for 海关数据分析、进出口趋势、贸易金额变化、原产地、目的国、贸易伙伴、商品、注册地、贸易方式、双数量、重量单价、数量单价、价格波动、市场集中度或变化驱动分析.
---

# 海关贸易数据报告

把中国海关导出的 CSV/XLSX 表格转换为可复核的 `report.md` 和本地 SVG 图表。

## 快速流程

1. 读取输入文件并确认用户关心的业务问题。用户未指定时，默认做完整多维分析。
2. 运行分析脚本：

```bash
python3 .agents/skills/customs-trade-report/scripts/analyze_customs.py \
  "/absolute/path/to/input.csv" \
  --output "00- 草稿/海关数据报告/{文件名}"
```

3. 打开生成的 `report.md`，检查口径说明、异常提示、图表和结论。
4. 根据用户问题补充解释，但不得把相关性写成因果，也不得猜测表格未提供的进出口方向。
5. 返回报告路径，并用 3-6 条简短结论概括最重要发现。

## 输出约定

默认输出到：

```text
00- 草稿/海关数据报告/{文件名}/
├── report.md
└── charts/
    ├── monthly-trend.svg
    ├── partner-top.svg
    └── ...
```

脚本支持：

- CSV：自动尝试 `UTF-8-SIG`、`GB18030`、`UTF-16`
- XLSX：使用环境中的 `openpyxl`
- 常见海关字段别名自动映射
- 单月或字段缺失时自动跳过不适用分析
- 第一数量、第二数量按各自计量单位独立计算加权单价

## 口径规则

- 先读 [references/customs-fields.md](references/customs-fields.md)，确认字段语义。
- 需要解释指标或选择图表时，读 [references/analysis-methodology.md](references/analysis-methodology.md)。
- `贸易伙伴` 不自动等同于 `原产国` 或 `最终目的国`。只有存在明确字段时才分别分析。
- 表内没有 `进出口方向` 时，明确写“无法仅凭此表判断进口或出口”。
- 金额列不是美元时，保留原列名，不擅自换算币种。
- 单价只在数量大于 0 且计量单位唯一时计算；金额分子仅使用这些有效数量记录。
- 第一数量与第二数量分别分析。例如第一数量为“台”、第二数量为“千克”时，分别计算美元/台和美元/千克，不互相换算。
- 两个数量字段都有效时，额外计算双数量比值，例如平均千克/台，用于观察平均规格或重量变化。
- 月度加权单价是金额合计除以数量合计，不使用逐行单价的简单平均。
- 单价波动可能由真实价格、规格、市场或贸易方式结构变化共同造成，不直接解释为同款产品涨跌价。
- 最新月份明显低于历史水平时，提示可能是未完结月份，不直接判断需求骤降。

## 图表选择

按数据条件生成，而不是凑齐图表：

- 月度金额趋势：折线图
- 贸易伙伴、原产地、目的国、商品、注册地、贸易方式排名：横向条形图
- 首末期金额变化：正负变化条形图
- 多月份与主要贸易伙伴交叉：热力图
- 每个有效数量字段：数量趋势、加权单价趋势、价格波动、主要市场单价对比
- 两个有效数量字段：双数量比值趋势，例如平均千克/台
- 两个分类维度的主要流向：交叉组合表；需要进一步展示时可补充桑基图

## 手动定制

脚本常用参数：

```bash
python3 .agents/skills/customs-trade-report/scripts/analyze_customs.py INPUT \
  --output OUTPUT_DIR \
  --title "报告标题" \
  --flow-label "出口" \
  --top-n 10
```

`--flow-label` 只用于用户已确认进口/出口口径的情况。

## 完成检查

- 确认报告金额总计与源表汇总一致。
- 确认时间排序正确，最新月份是否可能不完整。
- 确认原产地、目的国、贸易伙伴没有被混用。
- 确认每个数量字段与自己的计量单位匹配，单价金额覆盖率合理。
- 确认所有 Markdown 图片路径可打开。
- 确认结论能由报告中的数字直接支撑。
