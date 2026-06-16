# Report Format

Every run must create `report.md`.

## Normalized Schema

Use these columns when merging domestic and overseas data:

```text
rank
region              # China, Overseas, Global
platform
result_type         # post, video, article, creator, account, hashtag, trend
query
title_or_handle
author_name
author_handle
url
published_at
followers
views
likes
comments
shares
reposts
reads
favorites
engagement_rate
summary
why_it_matters
source_provider
confidence          # high, medium, low
raw_file
```

## Markdown Structure

```markdown
# <keyword> 国内外社交媒体热点报告

生成时间：
关键词：
范围：
排序口径：

## 摘要

## Top 内容

| 排名 | 区域 | 平台 | 内容 | 作者 | 数据 | 链接 | 热点原因 |

## KOL / 账号线索

| 排名 | 区域 | 平台 | 账号 | 数据 | 链接 | 适配原因 |

## 趋势洞察

## 内容机会

## 数据缺口与限制

## 原始文件
```

If a section is not relevant, include a one-line note instead of omitting it. For example: “本次任务未做 KOL 明细查询。”
