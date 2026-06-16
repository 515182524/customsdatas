# Domestic Routing

Use `redfox-social-media` for Chinese social media. Read `/Users/lg/.codex/skills/redfox-social-media/SKILL.md`, then choose the original bundled skill from `references/catalog.md`.

## Common Routes

| Need | Route |
|---|---|
| 抖音关键词热门作品 | `douyin-search`, `douyin-realtime-search`, `douyin-daily-hot` |
| 抖音账号/KOL 明细 | `douyin-account-diagnosis`, `douyin-top-account`, `douyin-similar-account`, `douyin-works-crawler` |
| 小红书热门内容 | `xiaohongshu-search`, `xiaohongshu-crawler`, `xiaohongshu-dailytop`, `xiaohongshu-weeklytop`, `xiaohongshu-lowtop` |
| 小红书账号/KOL | `xiaohongshu-account-analyzer`, `xiaohongshu-top-account`, `xiaohongshu-similar-account` |
| 公众号爆款文章 | `wechat-search`, `gzh-search-crawler`, `wechat-10w-hot`, `wechat-original-hot` |
| 公众号账号/KOL | `wechat-account-analyzer`, `wechat-top-account`, `wechat-fastest-growing`, `wechat-similar-account` |
| B站/视频号 AI 热点 | `bili-ai-feed`, `wechat-channels-ai-feed` |
| 全网中文热搜 | `trending-hub`, `trending-hub-top10`, `cn-last30days` |
| 标题/封面/改写/违禁词 | RedFox title, cover, rewrite, prohibited-word, multi-wordcheck skills |

## Execution Rules

- Verify `REDFOX_API_KEY` without printing it.
- Prefer `scripts/redfox.py` and bundled source scripts over direct API calls.
- Always create or update the merged Markdown report.
- If RedFox source skill has date limits or confirmation rules, follow them unless the merged skill's row-display default is the only conflict.
